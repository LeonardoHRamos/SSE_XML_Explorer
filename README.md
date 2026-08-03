# SSE XML Explorer

Aplicação desktop para localizar registros XML em estações configuradas e apresentar os campos operacionais relevantes de forma rápida.

> Todos os nomes, endereços, identificadores e screenshots deste repositório são fictícios. Os endereços IP de exemplo pertencem aos blocos reservados para documentação.

## Objetivo

O projeto resolve, de forma genérica, a necessidade de consultar registros XML distribuídos em compartilhamentos Windows quando a busca manual em diretórios é lenta ou sujeita a erros.

## Funcionalidades

- pesquisa e seleção de estações;
- preenchimento automático do IP;
- consulta em thread para manter a interface responsiva;
- autenticação em compartilhamento Windows com timeout e verificação de retorno;
- busca recursiva do XML pelo KNR;
- parsing de data, hora, estação, operador e sequência;
- histórico em memória durante a sessão;
- abertura do XML encontrado e tratamento de erros.

## Arquitetura e stack

A interface em `app.py` carrega a configuração local e delega o acesso ao compartilhamento para `network_reader.py`. O XML encontrado é processado por `xml_parser.py`; `logger.py` centraliza logs seguros, sem credenciais nem conteúdo XML.

Stack: Python 3.10+, Tkinter, ttkbootstrap, python-dotenv e ElementTree da biblioteca padrão. A consulta de rede usa o comando `net use` do Windows.

## Estrutura

```text
.
├── app.py
├── network_reader.py
├── xml_parser.py
├── logger.py
├── utils/
├── config/
│   └── stations.example.json
├── images/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Instalação

No Windows, com Python disponível:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configuração

Copie `.env.example` para `.env` e substitua somente no arquivo local:

```dotenv
NETWORK_USERNAME=seu-usuario
NETWORK_PASSWORD=sua-senha
NETWORK_SHARE=nome-do-compartilhamento
XML_BASE_PATHS=caminho/relativo/um;caminho/relativo/dois
LOG_LEVEL=INFO
```

`XML_BASE_PATHS` aceita caminhos relativos ao compartilhamento, separados por ponto e vírgula. Não inclua credenciais ou configurações reais em commits.

Para estações, copie `config/stations.example.json` para `config/stations.local.json` e edite a cópia local:

```json
{
  "Minha estação": "192.0.2.10"
}
```

A aplicação procura primeiro `stations.local.json`, ignorado pelo Git. Na ausência dele, carrega o exemplo fictício apenas para demonstração da interface.

## Execução

```powershell
python app.py
```

Selecione uma estação, informe um KNR de exatamente oito dígitos e clique em **Consultar**. Acesso efetivo a compartilhamentos requer Windows, conectividade e permissões válidas.

## Segurança

- `.env` e `*.local.json` são ignorados;
- a senha não é incluída diretamente nos argumentos de `net use`;
- falhas não exibem a saída potencialmente sensível do comando;
- logs não contêm senha, credenciais, KNR, caminhos consultados ou XML completo;
- configurações e screenshots públicos usam somente dados fictícios.

Antes de publicar alterações futuras, revise código, histórico do Git, logs, imagens e artefatos gerados. Se uma captura contiver dado real, descarte-a e faça uma nova captura com dados fictícios; não cubra ou borre o conteúdo.

## Limitações

- autenticação e leitura de rede foram projetadas para compartilhamentos Windows;
- a busca recursiva pode ser lenta em árvores muito grandes;
- o histórico existe somente durante a sessão;
- as tags XML esperadas são `DAT`, `TIM`, `ABZ`, `EKS` e `BodyIdent`.

## Roadmap

- testes automatizados adicionais;
- cancelamento e progresso de buscas longas;
- limites configuráveis de profundidade e tempo de busca;
- suporte opcional a formatos XML mapeáveis;
- empacotamento reproduzível para distribuição.

