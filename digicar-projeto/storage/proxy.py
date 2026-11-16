from collections import OrderedDict
from threading import Lock, local

from .interfaces import ArquivoStorage


class CachedArquivoStorage(ArquivoStorage):
    """Proxy do padrao Proxy: mesma interface do servico real, com cache e conexao sob demanda.

    - Proxy de cache: guarda em memoria o conteudo ja buscado. Quando passa do limite
      de bytes, descarta o arquivo usado ha mais tempo (LRU).
    - Proxy virtual: conectar() so registra o pedido. A conexao real e aberta no
      primeiro acesso que o cache nao resolve; um acerto no cache nao toca no servico.

    Como implementa ArquivoStorage, o ArquivoService recebe o proxy sem perceber a troca.
    """

    def __init__(self, storage: ArquivoStorage, limite_bytes: int):
        if limite_bytes <= 0:
            raise ValueError("limite_bytes deve ser maior que zero")
        self._storage = storage  # referencia ao servico real
        self._limite_bytes = limite_bytes
        self._cache = OrderedDict()
        self._bytes_em_cache = 0
        # Aumenta a cada invalidacao. Uma busca que comecou antes de uma exclusao
        # nao pode devolver ao cache o arquivo que acabou de ser excluido.
        self._geracao = 0
        self._lock = Lock()
        # O proxy e compartilhado pelo StorageManager entre requisicoes (threads),
        # entao o estado da conexao e guardado por thread.
        self._conexao = local()

    # --- Proxy virtual: conexao sob demanda ---------------------------------

    def conectar(self) -> None:
        self._conexao.pendente = True

    def desconectar(self) -> None:
        if getattr(self._conexao, "aberta", False):
            self._storage.desconectar()
        self._conexao.pendente = False
        self._conexao.aberta = False

    def _servico(self) -> ArquivoStorage:
        if getattr(self._conexao, "pendente", False):
            self._conexao.pendente = False
            self._storage.conectar()
            self._conexao.aberta = True
        return self._storage

    # --- Operacoes da interface ---------------------------------------------

    def buscar(self, identificador: str) -> bytes:
        with self._lock:
            conteudo = self._cache.get(identificador)
            if conteudo is not None:
                self._cache.move_to_end(identificador)
                return conteudo
            geracao = self._geracao

        conteudo = self._servico().buscar(identificador)
        self._guardar(identificador, conteudo, geracao)
        return conteudo

    def existe(self, identificador: str) -> bool:
        with self._lock:
            if identificador in self._cache:
                return True
        return self._servico().existe(identificador)

    def salvar(self, nome: str, conteudo: bytes) -> str:
        try:
            identificador = self._servico().salvar(nome, conteudo)
        finally:
            # No disco local o nome e o identificador: salvar de novo sobrescreve o arquivo.
            self._invalidar(nome)
        self._invalidar(identificador)
        return identificador

    def excluir(self, identificador: str) -> None:
        try:
            self._servico().excluir(identificador)
        finally:
            self._invalidar(identificador)

    def limpar_cache(self) -> None:
        with self._lock:
            self._cache.clear()
            self._bytes_em_cache = 0
            self._geracao += 1

    # --- Cache --------------------------------------------------------------

    def _guardar(self, identificador: str, conteudo: bytes, geracao: int) -> None:
        tamanho = len(conteudo)
        if tamanho > self._limite_bytes:
            return
        with self._lock:
            if geracao != self._geracao or identificador in self._cache:
                return
            self._cache[identificador] = conteudo
            self._bytes_em_cache += tamanho
            while self._bytes_em_cache > self._limite_bytes:
                _, removido = self._cache.popitem(last=False)
                self._bytes_em_cache -= len(removido)

    def _invalidar(self, identificador: str) -> None:
        with self._lock:
            conteudo = self._cache.pop(identificador, None)
            if conteudo is not None:
                self._bytes_em_cache -= len(conteudo)
            self._geracao += 1
