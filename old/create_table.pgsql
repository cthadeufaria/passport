create table if not EXISTS public.dictionary (
    conta_contabil text,
    c_custo text,
    "key" text,
    class_conta text,
    agrupamento text,
    pnl text,
    payroll text
);

create table if not EXISTS public.ledger (
    "Nº Lçto" text,
    "Movimentação" numeric,
    "Empresa II" text,
    "Conta II" text,
    "C.Custo II" text,
    Empresa text,
    "Descri Empresa" text,
    Bandeira text,
    "Descri Bandeira" text,
    Produto text,
    "Descri Produto" text,
    "Conta Contabil" text,
    "Descri Conta Contabil" text,
    "Centro Custo" text,
    "Descri Centro Custo" text,
    Intercompany text,
    "Descri Intercompany" text,
    "Unidade Negocio" text,
    "Descri Unid Neg" text,
    Futuro2 text,
    "Descri Futuro2" text,
    "Data Contabil" date,
    "Data Postada" date,
    Moeda text,
    "Descri Linha" text,
    "Journal Batch" text,
    "Journal Entry" text,
    Fornecedor text,
    Item text,
    Mes text,
    "Criado Por" text,
    "Num Lin" text,
    "Postado Por" text,
    "Total Debito" numeric,
    "Total Credito" numeric,
    "Total Debito Conv" numeric,
    "Total Credito Conv" numeric,
    "Id da Linha" text,
    "Key" text,
    "Gerencial" integer,
    "Classe Conta" text,
    "Agrupamento" text,
    "PnL" text,
    "Payroll" text
);

create table if not EXISTS public.items (
    "Codigo Organizacao" text,
    "Nome Organizacao" text,
    "Codigo Item" text,
    "Descricao Item" text,
    "Comprador" text,
    "Categoria" text,
    "Conta Contabil" text,
    "Descricao Conta Contabil" text,
    "Utilizacao Fiscal" text,
    "Recuperacao Pis" text,
    "Recuperacao Cofins" text,
    "Data Criacao" date
);

