# Exercício: padrão Proxy

Implemente o padrão de projeto **Proxy** em Java usando um sistema que exibe
imagens. A ideia é que o programa consiga solicitar uma imagem sem carregar o
arquivo pesado imediatamente.

## Contexto

Uma galeria precisa exibir várias imagens. O carregamento real de uma imagem é
caro e demorado, portanto a galeria deve trabalhar inicialmente com uma
representação leve. O arquivo real só deve ser carregado quando a imagem for
efetivamente exibida.

O programa também deve informar quando o arquivo real foi carregado, para que
seja possível observar o comportamento do Proxy durante os testes.

## Objetivo

Crie uma implementação de **Proxy Virtual** que:

1. mantenha uma abstração comum para a imagem real e para o Proxy;
2. adie o carregamento do arquivo até a primeira solicitação de exibição;
3. encaminhe as solicitações do Proxy para o objeto real;
4. reutilize o mesmo objeto real nas exibições seguintes;
5. permita que o cliente use o Proxy sem conhecer a classe da imagem real.

## Organização sugerida

Você pode organizar os arquivos em um pacote como `proxy` ou em subpacotes:

- `Image`: contrato comum para o objeto real e o Proxy;
- `RealImage`: objeto que simula o carregamento e a exibição do arquivo;
- `ImageProxy`: objeto que controla o carregamento sob demanda;
- `Gallery` ou `Main`: cliente que solicita as imagens.

Os nomes acima são apenas uma sugestão. Escolha os nomes que fizerem sentido
para sua implementação.

## Comportamento esperado

Ao criar uma imagem na galeria:

- o arquivo não deve ser carregado ainda;
- o Proxy deve guardar somente as informações necessárias para localizar a
  imagem.

Na primeira chamada de exibição:

- o Proxy deve criar ou obter a imagem real;
- o carregamento deve ser informado no console;
- a imagem deve ser exibida.

Nas chamadas de exibição seguintes para a mesma imagem:

- o arquivo não deve ser carregado novamente;
- somente a exibição deve ser repetida.

## Roteiro de teste manual

No `Main`, monte um cenário que:

1. crie dois ou mais objetos de imagem usando o tipo da abstração;
2. mostre uma mensagem indicando que as imagens foram cadastradas;
3. exiba apenas a primeira imagem;
4. exiba a primeira imagem novamente;
5. exiba a segunda imagem;
6. compare a ordem das mensagens no console.

O resultado deve deixar evidente que:

- cadastrar uma imagem não dispara o carregamento;
- cada imagem é carregada no máximo uma vez;
- o cliente trabalha com a abstração, e não diretamente com a imagem real.

## Extensão opcional

Depois de concluir o Proxy Virtual, acrescente uma regra de proteção: somente
usuários autenticados podem exibir determinadas imagens. Essa segunda versão
deve continuar usando a mesma abstração e não deve exigir alterações no código
cliente que apenas exibe as imagens.

## Critérios de conclusão

- O cliente não instancia diretamente o objeto real.
- O Proxy e o objeto real seguem o mesmo contrato.
- O carregamento tardio pode ser observado no console.
- Uma mesma imagem real não é carregada duas vezes.
- A implementação demonstra claramente a diferença entre objeto real e Proxy.
