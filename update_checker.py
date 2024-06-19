# -*- coding: utf-8 -*-
import requests
import os
import zipfile
import io
import shutil


class Update:
    def get_github_version(self):
        url = "https://raw.githubusercontent.com/Murilovisk01/Furaozinho/main/version.txt"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception("Não foi possível verificar a versão no GitHub.")

    def download_and_extract_zip(self):
        url = "https://github.com/Murilovisk01/Furaozinho/archive/refs/heads/main.zip"
        response = requests.get(url)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall("update_temp")
            return True
        return False

    def update_files(self):
        temp_folder = "update_temp/Furaozinho-main"
        
        if not os.path.exists(temp_folder):
            raise Exception(f"Diretório temporário não encontrado: {temp_folder}")
        
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                src_path = os.path.join(root, file)
                relative_path = os.path.relpath(src_path, temp_folder)
                dest_path = os.path.join(".", relative_path)
                
                # Cria diretório de destino se não existir
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Substitui o arquivo
                shutil.move(src_path, dest_path)
                print(f"Arquivo atualizado: {dest_path}")

        # Limpeza do diretório temporário
        shutil.rmtree("update_temp")
        print("Diretório temporário limpo.")

    def get_local_version(self):
        if os.path.exists("version.txt"):
            with open("version.txt", "r") as f:
                return f.read().strip()
        return None

    def update_version(self):
        try:
            github_version = self.get_github_version()
            local_version = self.get_local_version()

            if local_version is None or github_version != local_version:
                print("Atualização disponível. Baixando a nova versão...")
                if self.download_and_extract_zip():
                    self.update_files()
                    print("Atualização concluída com sucesso!")
                else:
                    print("Erro ao baixar a atualização.")
            else:
                print("Você já está usando a versão mais recente.")
        except Exception as e:
            print(f"Erro ao verificar atualizações: {e}")

