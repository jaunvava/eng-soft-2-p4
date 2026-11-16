from threading import Lock

from django.conf import settings
from pymongo import MongoClient

from .local_adapter import LocalStorageAdapter
from .mongo_adapter import MongoStorageAdapter
from .proxy import CachedArquivoStorage


class StorageManager:
    """Singleton que guarda os adapters de armazenamento de arquivos."""

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        # Equivalente ao construtor privado: a unica forma de obter o objeto e get_instance().
        raise TypeError("Use StorageManager.get_instance()")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instancia = super().__new__(cls)
                    mongo_client = MongoClient(settings.MONGO_URI)

                    instancia._local_adapter = LocalStorageAdapter(settings.MEDIA_ROOT)
                    instancia._mongo_adapter = MongoStorageAdapter(
                        mongo_client,
                        database_name=settings.MONGO_DATABASE,
                    )
                    instancia._mongo_storage = cls._com_cache(instancia._mongo_adapter)
                    cls._instance = instancia
        return cls._instance

    @staticmethod
    def _com_cache(adapter):
        """Decide quem recebe o proxy: com STORAGE_CACHE_MAX_BYTES=0 o cache fica desligado."""
        limite = settings.STORAGE_CACHE_MAX_BYTES
        if limite <= 0:
            return adapter
        return CachedArquivoStorage(adapter, limite_bytes=limite)

    def get_local_adapter(self):
        return self._local_adapter

    def get_mongo_adapter(self):
        return self._mongo_adapter

    def get_mongo_storage(self):
        """GridFS para os clientes: o proxy de cache na frente do adapter (ou o adapter, se o cache estiver desligado)."""
        return self._mongo_storage

    def get_adapter_configurado(self):
        """Devolve o storage escolhido em FILE_STORAGE."""
        if settings.FILE_STORAGE == "mongo":
            return self._mongo_storage
        if settings.FILE_STORAGE == "local":
            return self._local_adapter
        raise ValueError("FILE_STORAGE inválido. Use 'local' ou 'mongo'.")
