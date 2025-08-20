# Sistema-de-banco-2.0
Sistema de banco modularizado, com novas funções e mais otimizado.

Objetivos do sistema:

# Criação de sistema bancário incluindo funções:
# Saque, depósito, extrato (verificar histórico), cadastrar usuário (cliente) e cadastrar conta bancária/corrente (vincular com usuário).

# Funções:

- Saque (keyword only) = saldo, valor, extrato, limite, numero_saques, limite_saques // Retorno = saldo e extrato;
- Depósito (positional only) = saldo, valor, extrato // Retorno = saldo e extrato;
- Extrato (positional only e keyword only) -> Argumentos posicionais = saldo // Argumentos nomeados = extrato;
- Criar Cliente = nome, data nascimento, cpf e endereço (string formato -> logradouro, nro, bairro, cidade/sigla estado) somente nros do CPF e não pode cadastrar dois usuários com o mesmo cpf;
- Criar conta corrente = agência, nro da conta e usuário -> nro da conta é sequencial, iniciando em 1. Agência é fixo "0001" usuário pode ter mais de uma conta, mas uma conta pertence a somente um usuário.

* OBS: para vincular um usuário a uma conta, filtar a lista de usuários buscando o número do cpf informado para cada usuário da lista.
