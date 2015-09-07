import time
import datetime

try:
    datetime.datetime.strptime('0', '%H')
except TypeError:
    # Fix for datetime issues with XBMC/Kodi
    class new_datetime(datetime.datetime):
        @classmethod
        def strptime(cls, dstring, dformat):
            return datetime.datetime(*(time.strptime(dstring, dformat)[0:6]))

    datetime.datetime = new_datetime

from peewee import peewee
import util

DATABASE_VERSION = 1

fn = peewee.fn

DBVersion = None
Song = None
Trivia = None
AudioFormatBumpers = None
RatingsBumpers = None
VideoBumpers = None
WatchedTrailers = None
WatchedTrivia = None


def migrateDB(DB, version):
    util.DEBUG_LOG('Migrating database from version {0} to {1}'.format(version, DATABASE_VERSION))
    from peewee.playhouse import migrate
    migrator = migrate.SqliteMigrator(DB)
    try:
        migrate.migrate(
            migrator.add_column('RatingsBumpers', 'style', peewee.CharField(default='Classic'))
        )
    except peewee.OperationalError:
        util.ERROR()


def checkDBVersion(DB):
    vm = DBVersion.get_or_create(id=1, defaults={'version': 0})[0]
    if vm.version < DATABASE_VERSION:
        migrateDB(DB, vm.version)
        vm.update(version=DATABASE_VERSION).execute()


def initialize(path=None):
    util.callback(None, 'Creating/updating database...')

    global DBVersion
    global Song
    global Trivia
    global AudioFormatBumpers
    global RatingsBumpers
    global VideoBumpers
    global WatchedTrailers
    global WatchedTrivia

    ###########################################################################################
    # Watched Database
    ###########################################################################################
    DB = peewee.SqliteDatabase(util.pathJoin(path or util.STORAGE_PATH, 'content.db'))

    class DBVersion(peewee.Model):
        version = peewee.IntegerField(default=0)

        class Meta:
            database = DB

    DBVersion.create_table(fail_silently=True)

    checkDBVersion(DB)

    class ContentBase(peewee.Model):
        name = peewee.CharField()
        accessed = peewee.DateTimeField(null=True)
        pack = peewee.TextField(null=True)

        class Meta:
            database = DB

    util.callback(' - Music')

    class Song(ContentBase):
        rating = peewee.CharField(null=True)
        genre = peewee.CharField(null=True)
        year = peewee.CharField(null=True)

        path = peewee.CharField(unique=True)
        duration = peewee.FloatField(default=0)

    Song.create_table(fail_silently=True)

    util.callback(' - Tivia')

    class Trivia(ContentBase):
        type = peewee.CharField()

        TID = peewee.CharField(unique=True)

        rating = peewee.CharField(null=True)
        genre = peewee.CharField(null=True)
        year = peewee.CharField(null=True)
        duration = peewee.FloatField(default=0)

        questionPath = peewee.CharField(unique=True, null=True)
        cluePath0 = peewee.CharField(unique=True, null=True)
        cluePath1 = peewee.CharField(unique=True, null=True)
        cluePath2 = peewee.CharField(unique=True, null=True)
        cluePath3 = peewee.CharField(unique=True, null=True)
        cluePath4 = peewee.CharField(unique=True, null=True)
        cluePath5 = peewee.CharField(unique=True, null=True)
        cluePath6 = peewee.CharField(unique=True, null=True)
        cluePath7 = peewee.CharField(unique=True, null=True)
        cluePath8 = peewee.CharField(unique=True, null=True)
        cluePath9 = peewee.CharField(unique=True, null=True)
        answerPath = peewee.CharField(unique=True, null=True)

    Trivia.create_table(fail_silently=True)

    util.callback(' - AudioFormatBumpers')

    class BumperBase(ContentBase):
        is3D = peewee.BooleanField(default=False)
        isImage = peewee.BooleanField(default=False)
        path = peewee.CharField(unique=True)

    class AudioFormatBumpers(BumperBase):
        format = peewee.CharField()

    AudioFormatBumpers.create_table(fail_silently=True)

    util.callback(' - RatingsBumpers')

    class RatingsBumpers(BumperBase):
        system = peewee.CharField(default='MPAA')
        style = peewee.CharField(default='Classic')

    RatingsBumpers.create_table(fail_silently=True)

    util.callback(' - VideoBumpers')

    class VideoBumpers(BumperBase):
        type = peewee.CharField()

        rating = peewee.CharField(null=True)
        genre = peewee.CharField(null=True)
        year = peewee.CharField(null=True)

    VideoBumpers.create_table(fail_silently=True)

    ###########################################################################################
    # Watched Database
    ###########################################################################################
    W_DB = peewee.SqliteDatabase(util.pathJoin(path or util.STORAGE_PATH, 'watched.db'))

    class WatchedBase(peewee.Model):
        WID = peewee.CharField(unique=True)
        watched = peewee.BooleanField(default=False)
        date = peewee.DateTimeField(default=datetime.date(1900, 1, 1))

        class Meta:
            database = W_DB

    class WatchedTrailers(WatchedBase):
        source = peewee.CharField()
        rating = peewee.CharField(null=True)
        genres = peewee.CharField(null=True)
        title = peewee.CharField()
        url = peewee.CharField()
        userAgent = peewee.CharField(null=True)

    WatchedTrailers.create_table(fail_silently=True)

    util.callback(' - Trailers (watched status)')

    class WatchedTrivia(WatchedBase):
        pass

    WatchedTrivia.create_table(fail_silently=True)

    util.callback(' - Trivia (watched status)')

    util.callback(None, 'Database created')
