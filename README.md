# Projeto Final Tokio School Python 2023

## Resumo:

A Luxury Wheels, é uma empresa de aluguer de carros que deseja desenvolver um site, onde os clientes deverão conseguir registar-se e alugar um veículo, e uma app para a gestão da frota, a partir do qual a empresa consiga gerir todos os seus veículos.

- Classes
- Base de Dados
- Export Excel ou CSV
- Programas de decisão
- Criação de gráficos

Estrutura do site:
- BD de carros e motas
- BD de clientes
- BD de veículos por categoria (gold, silver e económico)
- Programas a criar:
- Sistema de aluguer
- Cliente terá determinado a categoria, consoante o categoria pode ter melhores carros
 
Estrutura da app:
- BD de carros e motas
- Programas a criar:
- Sistema de aluguer
- Carro disponível a partir da data xx/xx/xxxx
- Manutenção
- Após x utilizações, o veículo terá de ser enviado para a manutenção
- Alerta de necessidade de levar os veículos à manutenção
- Legalização
- 30 dias para legalizar (carro) pelo Estado
- Por exemplo, 5 em 5 anos, deve voltar a ser legalizado
- Parametrizar o alerta que informa a necessidade do aumento do estoque.
- Aspeto financeiro
- Entrada e saída de dinheiro


O objetivo principal é criar um site para o sistema de aluguel de veículos funcione normalmente, se for possível criar um app para a empresa fazer o gerenciamento do negócio e integrar tudo com a base de dados do site.

## Instruções:

- Após fazer o download completo de todo o conteúdo e descompactá-lo, acesse o caminho do diretório pelo temrinal;

- Crie um ambiente virtual em Python;

    python -m venv .venv

- Active o ambiente virtual;

    source .venv/bin/activate

- Instale todos os binários necessários;

    pip install -r requirements.txt --upgrade

- Inicie a aplicação Python para por o servidor Flask online;

    python app.py

- Para funcionar correctamente é necessário antes de tudo registar no Painel de Administração as categorias Gold, Silver e Económico;

- Somente para a fase desenvolvimento foi instituído um login padrão para o admin dentro da URL 'admin';

    login: "admin"
    password: "password"