import os

class Queue:
    def __init__(self, path):
        self.path = path
        with open(self.path, 'a'):
            pass
        self.lines = self.count_lines()
    
    def queue(self, line):
        with open(self.path, 'a') as file:
            file.write(line + '\n')
            self.lines += 1
            file.flush()  # Garante que os dados sejam gravados no arquivo imediatamente
            
    def dequeue(self):
        if self.lines == 0:
            return None

        first_line = None
        temp_path = self.path + '.tmp'
        with open(self.path, 'r') as file, open(temp_path, 'w') as temp_file:
            # Leitura do primeiro elemento (primeira linha)
            first_line = file.readline().strip() 
            # Copia as linhas restantes para o arquivo temporário
            for line in file:
                temp_file.write(line)
        
        # Substituição do arquivo original pelo arquivo temporário
        os.replace(temp_path, self.path)
        self.lines -= 1
        return first_line
    
    def count_lines(self):
        count = 0
        with open(self.path, 'r') as file:
            for _ in file:
                count += 1
        return count