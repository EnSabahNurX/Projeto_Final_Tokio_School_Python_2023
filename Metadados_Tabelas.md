O arquivo `models.py` define os modelos de dados para o aplicativo Flask. Aqui estão as tabelas e suas colunas correspondentes, juntamente com uma breve descrição de cada uma delas:

## Tabela `categorias`

- **nome**: Uma coluna que armazena o nome da categoria.
  - Tipo de Dados: String (50 caracteres)
  - Restrições: Não nulo, único.

Esta tabela armazena informações sobre as categorias de veículos disponíveis.

## Tabela `veiculos`

- **id**: Uma coluna que serve como chave primária para os veículos.
  - Tipo de Dados: Integer
  - Restrições: Chave Primária

- **type**: Uma coluna que armazena o tipo de veículo (Carro ou Mota).
  - Tipo de Dados: Enumeração (VehicleType)
  - Restrições: Não nulo

- **brand**: Uma coluna que armazena a marca do veículo.
  - Tipo de Dados: String (100 caracteres)
  - Restrições: Não nulo

- **model**: Uma coluna que armazena o modelo do veículo.
  - Tipo de Dados: String (100 caracteres)
  - Restrições: Não nulo

- **year**: Uma coluna que armazena o ano de fabricação do veículo.
  - Tipo de Dados: Integer
  - Restrições: Não nulo

- **price_per_day**: Uma coluna que armazena o preço por dia para alugar o veículo.
  - Tipo de Dados: Float
  - Restrições: Não nulo

- **status**: Uma coluna booleana que indica se o veículo está disponível ou não.
  - Tipo de Dados: Boolean
  - Valor Padrão: Verdadeiro

- **in_maintenance**: Uma coluna booleana que indica se o veículo está em manutenção.
  - Tipo de Dados: Boolean
  - Valor Padrão: Falso

- **last_maintenance_date**: Uma coluna que armazena a data da última manutenção.
  - Tipo de Dados: Data

- **next_maintenance_date**: Uma coluna que armazena a data da próxima manutenção.
  - Tipo de Dados: Data

- **maintenance_history**: Uma coluna que armazena o histórico de manutenções.
  - Tipo de Dados: String (1000 caracteres)
  - Valor Padrão: Vazio

- **last_legalization_date**: Uma coluna que armazena a data da última legalização.
  - Tipo de Dados: Data

- **next_legalization_date**: Uma coluna que armazena a data da próxima legalização.
  - Tipo de Dados: Data

- **legalization_history**: Uma coluna que armazena o histórico de legalizações.
  - Tipo de Dados: String (1000 caracteres)
  - Valor Padrão: Vazio

- **imagens**: Uma coluna que armazena os caminhos das imagens do veículo.
  - Tipo de Dados: String (1000 caracteres)

- **available_from**: Uma coluna que armazena a data de disponibilidade do veículo.
  - Tipo de Dados: Data
  - Pode ser nulo

- **num_uses**: Uma coluna que armazena o número de vezes que o veículo foi usado.
  - Tipo de Dados: Integer
  - Valor Padrão: 0

- **max_uses_before_maintenance**: Uma coluna que armazena o número máximo de usos antes da manutenção.
  - Tipo de Dados: Integer
  - Valor Padrão: 50

- **categoria_id**: Uma coluna que armazena o ID da categoria do veículo (chave estrangeira para a tabela `categorias`).
  - Tipo de Dados: Integer
  - Restrições: Não nulo

- **categoria**: Uma coluna que estabelece uma relação com a tabela `categorias` e representa a categoria do veículo.
  - Tipo de Dados: Relacionamento com Categoria

Esta tabela armazena informações sobre os veículos disponíveis para aluguel, incluindo detalhes sobre manutenção, legalização e categorias.

## Tabela `clientes`

- **id**: Uma coluna que serve como chave primária para os clientes.
  - Tipo de Dados: Integer
  - Restrições: Chave Primária

- **nome**: Uma coluna que armazena o nome do cliente.
  - Tipo de Dados: String (100 caracteres)
  - Restrições: Não nulo

- **apelido**: Uma coluna que armazena o apelido do cliente.
  - Tipo de Dados: String (100 caracteres)
  - Restrições: Não nulo

- **email**: Uma coluna que armazena o endereço de e-mail do cliente.
  - Tipo de Dados: String (100 caracteres)
  - Restrições: Não nulo, único

- **telefone**: Uma coluna que armazena o número de telefone do cliente.
  - Tipo de Dados: String (20 caracteres)
  - Restrições: Não nulo

- **data_nascimento**: Uma coluna que armazena a data de nascimento do cliente.
  - Tipo de Dados: Data
  - Restrições: Não nulo

- **morada**: Uma coluna que armazena o endereço de morada do cliente.
  - Tipo de Dados: String (200 caracteres)
  - Restrições: Não nulo

- **nif**: Uma coluna que armazena o NIF (Número de Identificação Fiscal) do cliente.
  - Tipo de Dados: Integer
  - Restrições: Não nulo, único

- **price_per_day**: Uma coluna que armazena o preço por dia para alugar veículos (não está claro se esta coluna é usada no contexto de clientes).
  - Tipo de Dados: Float
  - Restrições: Não nulo, padrão 50

- **password**: Uma coluna que armazena a senha do cliente.
  - Tipo de Dados: String (100 caracteres)
  - Restrições: Não nulo

- **categoria**: Uma coluna que armazena a categoria do cliente (não está claro se esta coluna é usada no contexto de clientes).
  - Tipo de Dados: String (20 caracteres)
  - Restrições: Não nulo, padrão "Económico"

Esta tabela armazena informações sobre os clientes, incluindo detalhes pessoais e de contato.

# Classe para o modelo de Reserva

A classe `Reservation` define o modelo de dados para as reservas de veículos no seu aplicativo Flask. Abaixo estão as informações sobre a tabela e suas colunas correspondentes:

## Tabela `reservations`

- **id**: Uma coluna que serve como chave primária para as reservas.
  - Tipo de Dados: Integer
  - Restrições: Chave Primária

- **customer_id**: Uma coluna que armazena o ID do cliente que fez a reserva (chave estrangeira para a tabela `clientes`).
  - Tipo de Dados: Integer
  - Restrições: Não nulo

- **vehicle_id**: Uma coluna que armazena o ID do veículo reservado (chave estrangeira para a tabela `veiculos`).
  - Tipo de Dados: Integer
  - Restrições: Não nulo

- **status**: Uma coluna que armazena o status da reserva.
  - Tipo de Dados: String (20 caracteres)
  - Restrições: Não nulo, padrão "Ativa"

- **start_date**: Uma coluna que armazena a data de início da reserva.
  - Tipo de Dados: Data
  - Restrições: Não nulo

- **start_time**: Uma coluna que armazena a hora de início da reserva.
  - Tipo de Dados: Hora
  - Restrições: Não nulo

- **end_date**: Uma coluna que armazena a data de término da reserva.
  - Tipo de Dados: Data
  - Restrições: Não nulo

- **end_time**: Uma coluna que armazena a hora de término da reserva.
  - Tipo de Dados: Hora
  - Restrições: Não nulo

- **duration**: Uma coluna que armazena a duração da reserva em minutos.
  - Tipo de Dados: Integer
  - Restrições: Não nulo

- **price**: Uma coluna que armazena o preço total da reserva.
  - Tipo de Dados: Float
  - Restrições: Não nulo

### Métodos

- **add_reservations()**: Um método que adiciona a reserva ao banco de dados.
  - Comportamento: Adiciona a reserva atual ao banco de dados.

- **update_completed_reservations()**: Um método que atualiza o status das reservas concluídas.
  - Comportamento: Identifica as reservas cuja data de término é anterior à data atual e cujo status não é "Concluída". Em seguida, atualiza o status dessas reservas para "Concluída" no banco de dados.

Esta classe representa as reservas de veículos feitas pelos clientes no seu aplicativo e inclui métodos para adicionar e atualizar o status das reservas.
