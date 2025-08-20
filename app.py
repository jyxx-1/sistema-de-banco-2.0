# Criação de sistema bancário incluindo funções:
# Saque, depósito, extrato (verificar histórico), cadastrar usuário (cliente) e 
# cadastrar conta bancária/corrente (vincular com usuário)

# Funções:

# Saque (keyword only) = saldo, valor, extrato, limite, numero_saques, limite_saques // Retorno = saldo e extrato.
# Depósito (positional only) = saldo, valor, extrato // Retorno = saldo e extrato.
# Extrato (positional only e keyword only) -> Argumentos posicionais = saldo // Argumentos nomeados = extrato.

# Criar Cliente = nome, data nascimento, cpf e endereço (string formato -> logradouro, nro, bairro, cidade/sigla estado) ->
# -> Somente nros do CPF e não pode cadastrar dois usuários com o mesmo cpf.

# Criar conta corrente = agência, nro da conta e usuário -> nro da conta é sequencial, iniciando em 1. Agência é fixo 0001 ->
# -> usuário pode ter mais de uma conta, mas uma conta pertence a somente um usuário.

# OBS: para vincular um usuário a uma conta, filtre a lista de usuários buscando o número do cpf informado para cada ->
# -> usuário da lista.

# ===================================== DESENVOLVIMENTO =====================================

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

# ===============================
# Modelos de dados
# ===============================

@dataclass
class Usuario:
    nome: str
    data_nascimento: date
    cpf: str  # apenas dígitos
    endereco: str  # "logradouro, nro, bairro, cidade/UF"


@dataclass
class Conta:
    agencia: str = "0001"
    numero: int = 0
    cpf_titular: str = ""
    saldo: float = 0.0
    extrato: List[str] = field(default_factory=list)  # histórico de lançamentos
    numero_saques_hoje: int = 0
    data_referencia_saques: Optional[date] = None


# ===============================
# Utilidades
# ===============================

def _hoje() -> date:
    return datetime.now().date()


def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def somente_digitos(texto: str) -> str:
    return "".join(ch for ch in texto if ch.isdigit())


# ===============================
# Cadastro de usuários e contas
# ===============================

def filtrar_usuario_por_cpf(cpf: str, usuarios: Dict[str, Usuario]) -> Optional[Usuario]:
    cpf_num = somente_digitos(cpf)
    return usuarios.get(cpf_num)


def criar_usuario(nome: str, data_nascimento_str: str, cpf: str, endereco: str,
                  /, *, usuarios: Dict[str, Usuario]) -> Usuario:
    """Cria e registra um usuário se o CPF (apenas números) ainda não existir.
    - data_nascimento_str: "DD/MM/AAAA"
    """
    cpf_num = somente_digitos(cpf)
    if not cpf_num:
        raise ValueError("CPF inválido: informe ao menos um dígito.")
    if cpf_num in usuarios:
        raise ValueError("Já existe usuário com este CPF.")

    try:
        dn = datetime.strptime(data_nascimento_str, "%d/%m/%Y").date()
    except ValueError as e:
        raise ValueError("Data de nascimento inválida. Use o formato DD/MM/AAAA.") from e

    usuario = Usuario(nome=nome.strip(), data_nascimento=dn, cpf=cpf_num, endereco=endereco.strip())
    usuarios[cpf_num] = usuario
    return usuario


def criar_conta(cpf_titular: str, /, *, usuarios: Dict[str, Usuario], contas: Dict[int, Conta]) -> Conta:
    """Cria uma conta vinculada a um usuário existente. Agência fixa "0001".
    Número da conta é sequencial, iniciando em 1.
    """
    cpf_num = somente_digitos(cpf_titular)
    if cpf_num not in usuarios:
        raise ValueError("Usuário não encontrado para o CPF informado.")

    proximo_numero = 1 if not contas else (max(contas.keys()) + 1)
    conta = Conta(agencia="0001", numero=proximo_numero, cpf_titular=cpf_num)
    contas[proximo_numero] = conta
    return conta


# ===============================
# Operações bancárias (com / e *)
# ===============================

def deposito(saldo: float, valor: float, extrato: List[str], /) -> Tuple[float, List[str]]:
    """Depósito (positional-only): saldo, valor, extrato -> retorna (saldo, extrato)"""
    if valor <= 0:
        raise ValueError("Valor de depósito deve ser positivo.")
    saldo += valor
    extrato.append(f"{datetime.now():%d/%m/%Y %H:%M} | DEPÓSITO   | +{formatar_moeda(valor)} | Saldo: {formatar_moeda(saldo)}")
    return saldo, extrato


def _resetar_contagem_saques_se_novo_dia(conta: Conta) -> None:
    hoje = _hoje()
    if conta.data_referencia_saques != hoje:
        conta.data_referencia_saques = hoje
        conta.numero_saques_hoje = 0


def saque(*, saldo: float, valor: float, extrato: List[str], limite: float,
          numero_saques: int, limite_saques: int) -> Tuple[float, List[str], int]:
    """Saque (keyword-only): retorna (saldo, extrato, numero_saques_atualizado)
    Regras:
    - valor > 0
    - valor <= saldo
    - valor <= limite por operação
    - numero_saques < limite_saques
    """
    if valor <= 0:
        raise ValueError("Valor de saque deve ser positivo.")
    if valor > saldo:
        raise ValueError("Saldo insuficiente para saque.")
    if valor > limite:
        raise ValueError("Valor excede o limite por saque.")
    if numero_saques >= limite_saques:
        raise ValueError("Limite de saques do período atingido.")

    saldo -= valor
    numero_saques += 1
    extrato.append(f"{datetime.now():%d/%m/%Y %H:%M} | SAQUE      | -{formatar_moeda(valor)} | Saldo: {formatar_moeda(saldo)}")
    return saldo, extrato, numero_saques


def exibir_extrato(saldo: float, /, *, extrato: List[str]) -> str:
    """Extrato (positional-only e keyword-only):
    - saldo (posicional)
    - extrato (nomeado)
    Retorna uma string formatada com o histórico e o saldo atual.
    """
    linhas = ["\n========== EXTRATO =========="]
    if extrato:
        linhas.extend(extrato)
    else:
        linhas.append("(Sem movimentações)")
    linhas.append(f"Saldo atual: {formatar_moeda(saldo)}")
    linhas.append("=============================\n")
    return "\n".join(linhas)


# ===============================
# Fachadas por conta (encapsulam as funções primitivas)
# ===============================

def depositar_na_conta(conta: Conta, valor: float) -> None:
    conta.saldo, conta.extrato = deposito(conta.saldo, valor, conta.extrato)


def sacar_da_conta(conta: Conta, valor: float, *, limite_por_saque: float, limite_saques_dia: int) -> None:
    _resetar_contagem_saques_se_novo_dia(conta)
    novo_saldo, novo_extrato, novo_num = saque(
        saldo=conta.saldo,
        valor=valor,
        extrato=conta.extrato,
        limite=limite_por_saque,
        numero_saques=conta.numero_saques_hoje,
        limite_saques=limite_saques_dia,
    )
    conta.saldo = novo_saldo
    conta.extrato = novo_extrato
    conta.numero_saques_hoje = novo_num


def extrato_da_conta(conta: Conta) -> str:
    return exibir_extrato(conta.saldo, extrato=conta.extrato)


# ===============================
# UI (CLI)
# ===============================

MENU = """
\n========== MENU ==========
[d] Depositar
[s] Sacar
[e] Extrato
[nu] Novo usuário
[nc] Nova conta
[lc] Listar contas
[ac] Acessar conta por número
[q] Sair
> """


def listar_contas(contas: Dict[int, Conta], usuarios: Dict[str, Usuario]) -> str:
    if not contas:
        return "\n(Nenhuma conta cadastrada)\n"
    linhas = ["\n======= CONTAS CADASTRADAS ======="]
    for n, c in sorted(contas.items()):
        u = usuarios.get(c.cpf_titular)
        nome = u.nome if u else "(Desconhecido)"
        linhas.append(
            f"Agência: {c.agencia} | Conta: {c.numero:06d} | Titular: {nome} (CPF {c.cpf_titular}) | Saldo: {formatar_moeda(c.saldo)}"
        )
    linhas.append("===================================\n")
    return "\n".join(linhas)


def _input_float(msg: str) -> float:
    valor_str = input(msg).replace(",", ".").strip()
    try:
        return float(valor_str)
    except ValueError:
        raise ValueError("Valor numérico inválido.")


def main() -> None:
    usuarios: Dict[str, Usuario] = {}
    contas: Dict[int, Conta] = {}

    conta_atual: Optional[Conta] = None
    limite_por_saque = 500.0
    limite_saques_dia = 3

    print("\nBem-vindo ao Sistema Bancário 2.0! Agência fixa 0001.\n")

    while True:
        try:
            opcao = input(MENU).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo... Até logo!")
            break

        try:
            if opcao == "d":
                if not conta_atual:
                    print("\nNenhuma conta ativa. Use [ac] para acessar uma conta ou crie uma em [nc].")
                    continue
                valor = _input_float("Valor do depósito: ")
                depositar_na_conta(conta_atual, valor)
                print("Depósito realizado com sucesso.")

            elif opcao == "s":
                if not conta_atual:
                    print("\nNenhuma conta ativa. Use [ac] para acessar uma conta ou crie uma em [nc].")
                    continue
                valor = _input_float("Valor do saque: ")
                sacar_da_conta(conta_atual, valor, limite_por_saque=limite_por_saque, limite_saques_dia=limite_saques_dia)
                print("Saque realizado com sucesso.")

            elif opcao == "e":
                if not conta_atual:
                    print("\nNenhuma conta ativa. Use [ac] para acessar uma conta ou crie uma em [nc].")
                    continue
                print(extrato_da_conta(conta_atual))

            elif opcao == "nu":
                nome = input("Nome completo: ").strip()
                data_nasc = input("Data de nascimento (DD/MM/AAAA): ").strip()
                cpf = input("CPF (somente números ou com máscara): ").strip()
                endereco = input("Endereço (logradouro, nro, bairro, cidade/UF): ").strip()
                usuario = criar_usuario(nome, data_nasc, cpf, endereco, usuarios=usuarios)
                print(f"Usuário criado: {usuario.nome} (CPF {usuario.cpf})")

            elif opcao == "nc":
                cpf = input("CPF do titular: ").strip()
                conta = criar_conta(cpf, usuarios=usuarios, contas=contas)
                print(f"Conta criada: Agência {conta.agencia} | Conta {conta.numero:06d} | Titular CPF {conta.cpf_titular}")

            elif opcao == "lc":
                print(listar_contas(contas, usuarios))

            elif opcao == "ac":
                if not contas:
                    print("\nNão há contas. Crie uma com [nc].")
                    continue
                try:
                    numero = int(input("Número da conta (apenas dígitos): ").strip())
                except ValueError:
                    print("Número inválido.")
                    continue
                conta_atual = contas.get(numero)
                if conta_atual:
                    u = usuarios.get(conta_atual.cpf_titular)
                    nome = u.nome if u else conta_atual.cpf_titular
                    print(f"Conta {conta_atual.numero:06d} acessada (Titular: {nome}).")
                else:
                    print("Conta não encontrada.")

            elif opcao == "q":
                print("\nSaindo... Obrigado por usar o Sistema Bancário 2.0!")
                break

            else:
                print("Opção inválida. Tente novamente.")

        except Exception as e:
            print(f"Erro: {e}")


if __name__ == "__main__":
    main()
