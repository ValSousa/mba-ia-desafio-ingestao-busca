from search import search_prompt

SAIR = {"sair", "exit", "quit"}


def main():
    try:
        chain = search_prompt()
    except Exception as e:
        chain = None
        print(f"Erro ao inicializar: {e}")

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print(f"Chat pronto. Faça sua pergunta (ou digite 'sair' para encerrar).\n")

    while True:
        pergunta = input("PERGUNTA: ").strip()

        if not pergunta:
            continue

        if pergunta.lower() in SAIR:
            break

        try:
            resposta = chain(pergunta)
        except Exception as e:
            resposta = f"Erro ao buscar resposta: {e}"

        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()
