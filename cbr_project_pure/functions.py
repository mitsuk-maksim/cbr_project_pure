import copy
import datetime
# import hashlib
import inspect
import os
import re
import subprocess
# import traceback
from collections import OrderedDict
# from media.functions import upload_report_handler
# from collections import namedtuple
from functools import wraps
from pprint import PrettyPrinter
from typing import Generic, TypeVar, Iterator, Dict, Type, Callable, Tuple

# import eyed3
import graphene
import pytz
# import telegram
# from PIL import Image as pil
from django.conf import settings
# from django.contrib.sites.models import Site
from django.db.models import QuerySet
from graphene import Argument
from graphene.types.field import Field
from graphene.types.objecttype import ObjectType, ObjectTypeOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.get_unbound_function import get_unbound_function
from graphene.utils.props import props
# from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_django.types import ErrorType
from graphql.utils.ast_to_dict import ast_to_dict
from graphql_jwt import exceptions
from graphql_jwt.decorators import context
# from telegram.error import InvalidToken, BadRequest

# from main.models import TelegramBot,File
# from media.models import Mediafile, MediafileValue, Value, Attribute


_Z = TypeVar("_Z")


class QueryType(Generic[_Z], QuerySet):
    def __iter__(self) -> Iterator[_Z]: ...


def deph_inspect(obj):
    exclude_entry = ['__setattr__', '__getattr__', '__delattr__', '__repr__', '__setitem__',
                     '__getitem__', '__new__', '__add__', '__call__', '__eq__', '__ge__',
                     '__getattribute__', '__setattribute__', '__delattribute__', '__delitem__',
                     '__getitem__', '__setitem__', '__gt__', '__hash__', '__le__', '__lt__', '__ne__',
                     '__reduce__', '__init__', '__iadd__', '__format__', '__imul__', '__iter__',
                     '__reversed__', '__rmul__', '__sizeof__', '__subclasshook__', '__init_subclass__',
                     '__iter__', '__mul__', '__reduce_ex__', '__contains__', '__get__', '__set__', '__del__',
                     'fromkeys', 'sort', 'append', 'clear', 'remove', 'pop', 'insert', 'index',
                     'extend', 'copy', 'reverse', 'get', 'setdefault', 'update', 'popitem', 'keys',
                     'values',
                     ]
    result = []
    for entry in inspect.getmembers(obj):
        if entry[0] in exclude_entry:
            continue
        sub_object = getattr(obj, entry[0])
        if entry[0] == '__doc__' or entry[1] in [dict, list, tuple, str, int]:
            {entry[0]: sub_object}
        elif 'object' in str(entry[1]):
            entry = {entry[0]: [e for e in inspect.getmembers(sub_object) if e[0] not in exclude_entry]}
        result.append(entry)
        pp = PrettyPrinter(indent=8, width=75, depth=4, compact=True)
    return pp.pformat(result)


def collect_fields(node, fragments):
    """Recursively collects fields from the AST
    Args:
        node (dict): A node in the AST
        fragments (dict): Fragment definitions
    Returns:
        A dict mapping each field found, along with their sub fields.
        {'name': {},
         'sentimentsPerLanguage': {'id': {},
                                   'name': {},
                                   'totalSentiments': {}},
         'slug': {}}
    """

    field = {}

    if node.get('selection_set'):
        for leaf in node['selection_set']['selections']:
            if leaf['kind'] == 'Field':
                field.update({
                    leaf['name']['value']: collect_fields(leaf, fragments)
                })
            elif leaf['kind'] == 'FragmentSpread':
                field.update(collect_fields(fragments[leaf['name']['value']],
                                            fragments))

    return field


def camel_case_convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def underscore_to_camelcase(word):
    words = word.split('_')
    return ''.join([words[0].lower()] + [x.capitalize() for x in words[1:]])


def get_graphql_fields(info):
    """A convenience function to call collect_fields with info
    Args:
        info (ResolveInfo)
    Returns:
        dict: Returned from collect_fields
    """

    fragments = {}
    node = ast_to_dict(info.field_asts[0])

    for name, value in info.fragments.items():
        fragments[name] = ast_to_dict(value)

    return collect_fields(node, fragments)


def graphql_permission(test_func, model=None):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            try:
                params = copy.deepcopy(kwargs)
            except TypeError:
                params = dict()
            id = params.get('input', {}).pop('id', None)
            if not id:
                id = params.pop('id', None)
            mutate = True if f.__name__.startswith('mutate') else False
            if test_func(context.user, context, id, model, mutate, **params):
                return f(*args, **kwargs)
            raise exceptions.PermissionDenied()

        return wrapper

    return decorator


# def token_for_device(uuid: str, device_type) -> str:
#     from devices.models import DeviceTypes
#
#     if device_type == DeviceTypes.DESKTOP:
#         salt = settings.DESKTOP_PLAYER_API_SALT
#     elif device_type == DeviceTypes.DESKTOPBOX:
#         salt = settings.DESKTOPBOX_PLAYER_API_SALT
#     elif device_type == DeviceTypes.ANDROID:
#         salt = settings.ANDROID_PLAYER_API_SALT
#     elif device_type == DeviceTypes.IOS:
#         salt = settings.IOS_PLAYER_API_SALT
#     elif device_type == DeviceTypes.WEBPLAYER:
#         salt = settings.WEB_PLAYER_API_SALT
#     elif device_type == DeviceTypes.NETCORE:
#         salt = settings.NETCORE_PLAYER_API_SALT
#     else:
#         salt = settings.MUSIC_BOX_API_SALT
#     token_prep = ''.join([uuid, salt])
#     return hashlib.sha1(token_prep.encode('UTF-8')).hexdigest()


class ErrorMutationMixin(object):
    ok = graphene.Boolean()
    errors = graphene.List(ErrorType)

    def resolve_ok(self, info):
        return not self.errors or not len(self.errors)

    def resolve_errors(self, info):
        return self.errors or []


def get_mutation_errors(cls, root, info, **kwargs):
    errors = list()
    for field, checkers in cls.validators.items():
        try:
            for check in checkers:
                res, message = check(kwargs[field])
                if not res:
                    errors.append(ErrorType(field=field,
                                            messages=[message]))
        except KeyError:
            continue
    return errors


def decorate_mutate_func(mutate_func, cls):
    def decorated_mutate(*args, **kwargs):
        errors = get_mutation_errors(cls, *args, **kwargs)
        if len(errors) == 0:
            return mutate_func(*args, **kwargs)
        return cls(errors=errors, ok=False)

    return decorated_mutate


class FieldResolverOptions(ObjectTypeOptions):
    arguments = None  # type: Dict[str, Argument]
    output = None  # type: Type[ObjectType]
    resolver = None  # type: Callable


class FieldResolver(ObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls, resolver=None, output=None, arguments=None,
                                    _meta=None, **options):
        if not _meta:
            _meta = FieldResolverOptions(cls)

        output = output or getattr(cls, 'Output', None)
        fields = {}
        if not output:
            # If output is defined, we don't need to get the fields
            fields = OrderedDict()
            for base in reversed(cls.__mro__):
                fields.update(
                    yank_fields_from_attrs(base.__dict__, _as=Field)
                )
            output = cls

        if not arguments:
            input_class = getattr(cls, 'Arguments', None)
            if input_class:
                arguments = props(input_class)
            else:
                arguments = {}

        if not resolver:
            _resolver = getattr(cls, 'query', None)
            assert _resolver, 'All field resolvers must define a query method'
            resolver = get_unbound_function(_resolver)

        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields

        _meta.output = output
        _meta.resolver = resolver
        _meta.arguments = arguments

        super(FieldResolver, cls).__init_subclass_with_meta__(
            _meta=_meta, **options)

    @classmethod
    def Field(cls, name=None, description=None, deprecation_reason=None, required=False):
        return Field(
            cls._meta.output,
            args=cls._meta.arguments,
            resolver=cls._meta.resolver,
            name=name,
            description=description,
            deprecation_reason=deprecation_reason,
            required=required,
        )


class CustomMutation(graphene.Mutation, ErrorMutationMixin):
    validators = dict()

    class Meta:
        abstract = True

    @classmethod
    def Field(
            cls, name=None, description=None, deprecation_reason=None, required=False
    ):
        """ Mount instance of mutation Field. """
        return Field(
            cls._meta.output,
            args=cls._meta.arguments,
            resolver=decorate_mutate_func(cls._meta.resolver, cls),
            name=name,
            description=description or cls._meta.description,
            deprecation_reason=deprecation_reason,
            required=required,
        )

    @classmethod
    def mutate(cls, root, info):
        return cls(ok=True, errors=[])


# class CustomSerializerMutation(SerializerMutation, ErrorMutationMixin):
#     permissions = ()
#
#     class Meta:
#         abstract = True
#
#     @staticmethod
#     def get_data(serializer, obj):
#         kwargs = {}
#         for f, field in serializer.fields.items():
#             if field.write_only:
#                 continue
#             try:
#                 kwargs[f] = field.get_attribute(obj)
#             except Exception:
#                 pass
#         return kwargs
#
#     @classmethod
#     def __init_subclass_with_meta__(cls, *args, **kwargs):
#         super(CustomSerializerMutation, cls).__init_subclass_with_meta__(*args, **kwargs)
#
#     @classmethod
#     def perform_mutate(cls, serializer, info):
#         obj = serializer.save()
#         return cls(errors=[], ok=True, **cls.get_data(serializer, obj))
#
#     @classmethod
#     def mutate_and_get_payload(cls, root, info, **input):
#
#         def permission_wrapper(target_fun, perm_functions):
#             if perm_functions:
#                 item_decorator = perm_functions.pop()
#                 return permission_wrapper(item_decorator(target_fun), perm_functions)
#             return target_fun
#
#         mutate_function_with_permissions = permission_wrapper(super().mutate_and_get_payload,
#                                                               list(cls.permissions))
#         return mutate_function_with_permissions(root, info, **input)


def field_from_graphql_message(message):
    field, error_type = None, None
    try:
        field = re.search('field\\s\"(.+?)\"', message).group(1)
        if field and 'found null' in message:
            return field, 'required field'
    except (IndexError, AttributeError):
        pass
    return field, error_type


# class TelegramLogger(object):
#     def __init__(self, type=None):
#         from main.models import TelegramBot, TelegramBotTypes
#
#         if type is None:
#             type = TelegramBotTypes.warnings
#         try:
#             self.settings = TelegramBot.objects.get(type_bot=type)
#         except Exception as es:
#             print('не удалось загрузить настройки telegram bot-а', es)
#             Settings = namedtuple('Settings', ('token', 'users'))
#             self.settings = Settings(token=settings.TELEGRAM_BOT_TOKEN, users=settings.TELEGRAM_DEV_USERS_IDS)
#         self.bot = self.get_bot()
#
#         self.env = self.env_name()
#
#     @staticmethod
#     def env_name():
#         if settings.DEBUG:
#             prefix = 'debug'
#         elif settings.PREPRODUCTION:
#             prefix = 'preprod'
#         else:
#             prefix = 'prod'
#         return f'{prefix} - (namespace: {settings.NAMESPACE})'
#
#     def get_bot(self):
#         try:
#             return telegram.Bot(token=self.settings.token)
#         except InvalidToken:
#             return None
#
#     def send_message(self, text):
#         from stream.functions import parse_int_param
#
#         def send(user_id, text):
#             if settings.DEBUG or settings.PREPRODUCTION:
#                 return
#             try:
#                 self.bot.send_message(user_id, text)
#             except BadRequest:
#                 pass
#             except Exception:
#                 pass
#
#         if self.bot:
#             trace = traceback.format_exc()
#             if len(trace) < 20:
#                 trace = ''
#             [send(user_id, '%s %s %s' % (self.env, text, trace)) for user_id in
#              parse_int_param(self.settings.users, many=True)]


def now_with_default_timezone():
    return datetime.datetime.now().astimezone(pytz.timezone(settings.TIME_ZONE))


# def image_convert(path, new_name, size):
#     try:
#         os.remove(new_name)
#     except Exception:
#         pass
#     try:
#         miniature = pil.open(path)
#     except IOError:
#         print('Не удалось открыть файл')
#         return False
#     if miniature.size[0] < size:
#         print('Размер исходного изображения ниже заданного')
#         return False
#     ratio = miniature.size[0] / size
#     miniature = miniature.resize(tuple(map(lambda x: int(x / ratio), miniature.size)), pil.ANTIALIAS)
#     miniature = miniature.convert("RGB")
#     miniature.save(new_name, quality=settings.IMAGE_CONVERT_QUALITY, optimize=True, progressive=True)
#     return True


# def tag_to_file(path, tags):
#     try:
#         tagfile = eyed3.load(path)
#     except Exception as es:
#         print('eyed3.load error', es)
#         return
#     if not tagfile:
#         return
#     tagfile.initTag()
#     if not tagfile.tag:
#         return
#     for key, val in tags.items():
#         if hasattr(tagfile.tag, key):
#             setattr(tagfile.tag, key, val)
#     os.chmod(path, 0o666)
#     tagfile.tag.save()
#     os.chmod(path, settings.DEFAULT_FILE_CHMOD)

#
# def tag_from_file(path, create_if_not_exist=True):
#     from main.tasks import tag_to_file_task
#
#     performer, title = settings.DEFAULT_PERFORMER_TITLE, settings.DEFAULT_TITLE
#     try:
#         tagfile = eyed3.load(path)
#     except Exception as es:
#         print(es)
#         return performer, title
#     if tagfile and tagfile.tag and tagfile.tag.title and tagfile.tag.artist:
#         title, performer = tagfile.tag.title, tagfile.tag.artist
#     if not tagfile and create_if_not_exist:
#         tag_to_file_task.apply_async((path, dict(title=title, performer=performer)), )
#     return performer, title


def command_run(command):
    subprocess.call(command, shell=True)


def convert_histogram_handler(source):
    filename, file_extension = os.path.splitext(source)
    if not os.path.exists(f'{filename}.dat'):
        subprocess.call('audiowaveform -i %s -o %s -b 8' % (source, f'{filename}.dat'), stdout=subprocess.PIPE,
                        shell=True)


# def translate(name):
#     symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
#                u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
#
#     tr = {ord(a): ord(b) for a, b in zip(*symbols)}
#     return name.translate(tr)
#
#
# def create_file_from_path(path, func, check_hash=True):
#     from main.models import File
#
#     hash = hashlib.md5(open(path, 'rb').read()).hexdigest()
#     try:
#         file = File.objects.filter(hash=hash)[0]
#         if file.exists:
#             return file
#         else:
#             file.delete()
#     except IndexError:
#         pass
#     filename, extension = os.path.splitext(path)
#     file = File.objects.create(file_writer_callback=lambda filename: func(path, filename), extension=extension)
#     file.calc_hash()
#     return file


# def get_rms(path):
#     from pydub import AudioSegment
#     from wave import Error
#     from pydub.exceptions import CouldntDecodeError
#
#     try:
#         return AudioSegment.from_file(path).rms
#     except (FileNotFoundError, CouldntDecodeError, Error):
#         return 0


# def get_sec_with_sound(segment, mediafile, reverse=False, rms_level=1000):
#     step = 1000
#     result = None
#     for sec in range(0, 5 * 60 * 1000, step):
#         if reverse:
#             start, end = -1 * sec - step, -1 * sec
#         else:
#             start, end = sec, sec + step
#         tmp_rms = segment[start: end].rms
#         if tmp_rms > rms_level:
#             result = mediafile.duration - sec if reverse else sec
#             break
#     return result
#
#
# def convert_normalize_128(source: str, path: str) -> None:
#     from pydub import AudioSegment
#     from pydub.exceptions import CouldntDecodeError
#
#     try:
#         segment = AudioSegment.from_file(source)
#     except (FileNotFoundError, CouldntDecodeError):
#         return
#     segment = segment.set_channels(2).set_frame_rate(44100).normalize()
#     with open(path, 'wb') as f:
#         segment.export(f, format='mp3', codec='libmp3lame', bitrate='128')
#
#
# def get_output_(cmd: str) -> Tuple[str, int]:
#     proc = subprocess.Popen(
#         cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
#     out, _ = proc.communicate()
#     return out, proc.returncode
#
#
# def convert_loudnorm(source: str, target: str,
#                      ilt: int = -16, lra: int = 11, mtp: float = -2.0) -> None:
#     preprocess_cmd = f'ffmpeg -i {source} -af loudnorm=I={ilt}:TP={mtp}:LRA={lra}:print_format=summary -f null -'
#     print(preprocess_cmd)
#     preprocess_resp, _ = get_output_(preprocess_cmd)
#     n_ilt = None
#     n_lra = None
#     n_mtp = None
#     n_thr = None
#     n_offset = None
#
#     for line in preprocess_resp.split('\n'):
#         if line.startswith('Input Integrated:'):
#             n_ilt = float(line.split(' ')[-2])
#         if line.startswith('Input True Peak:'):
#             n_mtp = float(line.split(' ')[-2])
#         if line.startswith('Input LRA:'):
#             n_lra = float(line.split(' ')[-2])
#         if line.startswith('Input Threshold:'):
#             n_thr = float(line.split(' ')[-2])
#         if line.startswith('Target Offset:'):
#             n_offset = float(line.split(' ')[-2])
#
#     cmd = f'ffmpeg -y -i {source} -ac 2 -af loudnorm=I={ilt}:TP={mtp}:LRA={lra}:' \
#           f'measured_I={n_ilt}:measured_TP={n_mtp}:measured_LRA={n_lra}:' \
#           f'measured_thresh={n_thr}:offset={n_offset}:linear=true:print_format=summary {target}'
#     print(cmd)
#     get_output_(cmd)
#
#
# def get_auto_mark(mediafile, rms_level=1000):
#     from pydub import AudioSegment
#     from wave import Error
#     from pydub.exceptions import CouldntDecodeError, TooManyMissingFrames
#     max_first_sec_shift = 0.3
#     marks = []
#     try:
#         segment = AudioSegment.from_file(mediafile.sourcefile.path)
#     except (FileNotFoundError, CouldntDecodeError, Error):
#         return marks
#     try:
#         last_sec = get_sec_with_sound(segment, mediafile, reverse=True, rms_level=rms_level)
#         first_sec = get_sec_with_sound(segment, mediafile, rms_level=rms_level)
#     except TooManyMissingFrames:
#         return marks
#     if first_sec and (first_sec > last_sec or first_sec > (max_first_sec_shift * mediafile.duration)):
#         print('invalid automarks')
#         return marks
#     if last_sec:
#         marks.append({'editable': True,
#                       'id': 'peaks.point.1',
#                       'labelText': 'End',
#                       'time': last_sec / 1000})
#     if first_sec:
#         marks.append({'editable': True,
#                       'id': 'peaks.point.0',
#                       'labelText': 'Start',
#                       'time': first_sec / 1000})
#     return marks
#
#
# def liquidsoap_log_to_csv():
#     from collections import Counter
#     from media.models import Mediafile
#     import csv
#
#     keys_compliance = {m.sourcefile.full_name: m.id_in_source + '.mp3' for m in Mediafile.objects.filter(type=0)}
#     print('keys compliance was created')
#     infile = open('key.log', 'r')
#     csv.register_dialect('unixpwd', delimiter=';', quoting=csv.QUOTE_NONE)
#     with open('key.csv', 'w+') as csvfile:
#         fieldnames = ['file', 'count']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='unixpwd')
#         writer.writeheader()
#         lines = []
#         for line in infile.readlines():
#             # print(line)
#             # dt_str = line.split(' [')[0]
#             # dt = datetime.datetime.strptime(dt_str, '%Y/%m/%d %H:%M:%S')
#             trname = line.split('/')[-1].replace('".\n', '')
#             lines.append(keys_compliance[trname])
#             # writer.writerow({'date': dt.str, 'file': keys_compliance[trname]})
#         lines = Counter(lines)
#         for line in lines:
#             writer.writerow({'file': line, 'count': lines[line]})
#
#
# def convert_data_to_graphql(data):
#     import copy
#     data = copy.deepcopy(data)
#     for k, value in list(data.items()):
#         value = data.pop(k)
#         if type(value) is datetime.datetime:
#             value = value.isoformat()
#         key = underscore_to_camelcase(k)
#         data.update({key: value})
#     return data
#
#
# def get_wiki_info_for_track(track_name: str, artist: str) -> dict:
#     import wikipedia
#     import wptools
#
#     try:
#         pages = wikipedia.search(f'{artist} {track_name}')
#         info = wptools.page(pages[0], silent=True).get_parse().data['infobox']
#         assert info['released']
#     except Exception:
#         info = None
#
#     return info
#
#
# def fill_writers_in_report(in_xlsx_path: str, out_xlsx_path: str):
#     import pandas as pd
#
#     tables = pd.read_excel(in_xlsx_path, sheet_name=['Отчет РАО', 'Отчет ВОИС'])
#
#     def process(string, label=False):
#         string = string.replace('{', '').replace('}', '')
#
#         def process_hlist(string_hlist):
#             result_hlist = []
#             for elem in re.split(r'\|', string_hlist.replace('hlist|', '')):
#                 if '[[' in elem and ']]' in elem:
#                     result_hlist.append(elem.replace('[[', '').replace(']]', ''))
#                 elif '[[' in elem and label:
#                     result_hlist.append(elem.replace('[[', ''))
#                 elif '[[' in elem and not label:
#                     continue
#                 elif ']]' in elem and label:
#                     continue
#                 elif ']]' in elem and not label:
#                     result_hlist.append(elem.replace(']]', ''))
#                 else:
#                     result_hlist.append(elem)
#
#             return result_hlist
#
#         if 'hlist' in string:
#             result = process_hlist(string)
#         else:
#             string = string.replace('*', '').replace('[', '').replace(']', '')
#
#             if 'flatlist' in string:
#                 string = string.replace('flatlist|\n', '')
#
#             result = []
#             for name in re.split(r'\n', string):
#                 res = re.split(r'\|', name)[0] if label else re.split(r'\|', name)[-1]
#                 res = re.sub(r'(^ )|( $)', '', res)
#                 result.append(res)
#
#         return ','.join(result)
#
#     none_count = 0
#     for i in range(tables['Отчет РАО'].shape[0]):
#         track_name = re.sub(r'(^ )|( $)', '', tables['Отчет РАО'].at[i, 'Название Фонограммы'])
#         artist = re.sub(r'(^ )|( $)', '', tables['Отчет РАО'].at[i, 'Исполнитель'])
#
#         tables['Отчет РАО'].at[i, 'Название Фонограммы'] = track_name
#         tables['Отчет РАО'].at[i, 'Исполнитель'] = artist
#
#         info = get_wiki_info_for_track(track_name, artist)
#
#         if info:
#             if 'writer' in info.keys():
#                 tables['Отчет РАО'].at[i, 'Автор слов'] = process(info['writer'])
#                 tables['Отчет ВОИС'].at[i, 'Автор Слов'] = process(info['writer'])
#
#             if 'label' in info.keys():
#                 tables['Отчет ВОИС'].at[i, 'Изготовитель Фонограммы'] = process(info['label'], label=True)
#
#             if 'compose' in info.keys():
#                 tables['Отчет РАО'].at[i, 'Автор музыки'] = process(info['compose'])
#                 tables['Отчет ВОИС'].at[i, 'Автор Музыки'] = process(info['compose'])
#             elif 'writer' in info.keys():
#                 tables['Отчет РАО'].at[i, 'Автор музыки'] = process(info['writer'])
#                 tables['Отчет ВОИС'].at[i, 'Автор Музыки'] = process(info['writer'])
#         else:
#             none_count += 1
#
#     writer = pd.ExcelWriter(out_xlsx_path)
#     for sheet_name, table in tables.items():
#         table.to_excel(writer, sheet_name=sheet_name, index=False)
#     writer.save()
#
#     print('Not found count:', none_count)
#
#
# def get_domain(request):
#     """
#     Return the correct main domain.
#     if DEBUG mode, return MAIN_SITE_ID.
#     :param request:
#     :return: domain
#     """
#     host = request.META.get('HTTP_HOST', '')
#     if settings.DEBUG:
#         try:
#             return Site.objects.get(id=settings.MAIN_SITE_ID).domain
#         except Site.DoesNotExist:
#             return Site.objects.first().domain
#     try:
#         main_site_id = settings.BY_MAIN_SITE_ID if '.by' in host else settings.MAIN_SITE_ID
#         domain = Site.objects.get(id=main_site_id).domain
#     except Site.DoesNotExist:
#         domain = Site.objects.first().domain
#     return domain
