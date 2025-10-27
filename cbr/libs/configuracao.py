import json
import os

# Salva configurações em um arquivo JSON para persistirem entre execuções do programa
class Configuracao:
    def __init__(self, nomeArquivo):
        self.nomeArquivo = nomeArquivo + ".json"
        if os.path.exists(self.nomeArquivo):
            try:
                self.carrega()
                print(f"Configurações carregadas: {self.nomeArquivo}")
            except json.JSONDecodeError:
                print("Erro ao ler o arquivo. Criando um novo.")
                self.config = []
        else:
            print("Arquivo de configurações não encontrado. Criando um novo.")
            self.config = []

    def limpa(self):
        """Apaga totalmente as configurações"""
        self.config = []
        self.salva()

    def salva(self):
        """Salva as configurações no arquivo JSON"""
        with open(self.nomeArquivo, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def carrega(self):
        """Carrega as configurações do arquivo JSON"""
        try:
            with open(self.nomeArquivo, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            print("Erro ao ler o arquivo. Criando um novo.")
            self.config = []

    def obtem(self, chave):
        """Lê um valor salvo de configuração"""
        for i in self.config:
            if i[0] == chave:
                return i[1]
        return None

    def insere(self, chave, valor):
        """Insere ou atualiza um valor de configuração"""
        for i in self.config:
            if i[0] == chave:
                i[1] = valor
                self.salva()
                return
        self.config.append([chave, valor])
        self.salva()


# ===== Exemplo de uso =====
if __name__ == "__main__":
    cfg = Configuracao("dados_sensor")
    cfg.insere("cor", [123, 45, 67, 255])  # Salvar uma RGBA
    print(cfg.obtem("cor"))                # -> [123, 45, 67, 255]
