import sys
import math

# Linha de comando simplificada:   
# cache_simulator <nsets> <bsize> <assoc> <subst> <flag_saida> arquivo_de_entrada.bin
def main():
    global miss_comp, miss_cap, miss_conf, hit, miss # Variaveis globais para contagem de miss

    miss_comp = 0
    miss_cap = 0
    miss_conf = 0
    hit = 0
    miss = 0

    # Possiveis erros de parametros
    if len(sys.argv) != 7:
        print("Parametros invalidos, formato correto: ") 
        print("python cache_simulator <nsets> <bsize> <assoc> <subst> <flag_saida> arquivo_de_entrada.bin")
        sys.exit(1)
    if (sys.argv[4] != "L" and sys.argv[4] != "l") and (sys.argv[4] != "R" and sys.argv[4] != "r") and (sys.argv[4] != "F" and sys.argv[4] != "f"):
        print("Parametro subst invalido, deve ser L, R ou F (lru, random ou fifo)")
        sys.exit(1)
    if sys.argv[5] != "0" and sys.argv[5] != "1":
        print("Parametro flag_saida invalido, deve ser 0 ou 1")
        sys.exit(1)
    
    # Abre o arquivo de entrada
    try:
        arquivo = open(sys.argv[6], "rb")
    except:
        print("Erro ao abrir o arquivo de entrada")
        sys.exit(1)

    nsets = int(sys.argv[1])
    bsize = int(sys.argv[2])    
    assoc = int(sys.argv[3])
    subst = sys.argv[4]
    flag_saida = int(sys.argv[5])
    arquivo = sys.argv[6]

    # Inicializa a cache
    cache_val = [[0] * assoc for _ in range(nsets)]  # array com o bit de validade de cada bloco
    cache_tag = [[-1] * assoc for _ in range(nsets)]  # array com a tag de cada bloco

    n_bit_offset = int(math.log2(bsize))    
    n_bit_indice= int(math.log2(nsets))

    n_bits_tag = 32 - n_bit_offset - n_bit_indice

    if assoc == 1:
        le_arquivo(arquivo, mapeamentoDir, n_bit_offset, n_bit_indice, cache_tag, cache_val, assoc, subst)
    elif nsets == 1:
        le_arquivo(arquivo, totalAssoc, n_bit_offset, n_bit_indice, cache_tag, cache_val, assoc, subst)
    else: # Ou quando assoc > 1 and nsets > 1
        le_arquivo(arquivo, mapAssoc, n_bit_offset, n_bit_indice, cache_tag, cache_val, assoc, subst)

    #  Total de acessos, Taxa de hit, Taxa de miss, Taxa de miss compulsório, Taxa de miss de capacidade, Taxa de miss de conflito
    miss = miss_comp + miss_cap + miss_conf 

    total_acessos = hit + miss
    taxa_hit = hit / total_acessos
    taxa_miss = miss / total_acessos
    taxa_miss_comp = miss_comp / miss
    taxa_miss_cap = miss_cap / miss
    taxa_miss_conf = miss_conf / miss

    if flag_saida == 1:
        print(f"{'Total acessos:':<25} {total_acessos}")
        print(f"{'Total hits:':<25} {hit}")
        print(f"{'Total misses:':<25} {miss}")
        print(f"{'Total misses comp:':<25} {miss_comp}")
        print(f"{'Total misses cap:':<25} {miss_cap}")
        print(f"{'Total misses conf:':<25} {miss_conf}")
        print(f"{'Taxa hit:':<25} {taxa_hit:.2%}")
        print(f"{'Taxa miss:':<25} {taxa_miss:.2%}")
        print(f"{'Taxa miss compulsório:':<25} {taxa_miss_comp:.2%}")
        print(f"{'Taxa miss de capacidade:':<25} {taxa_miss_cap:.2%}")
        print(f"{'Taxa miss de conflito:':<25} {taxa_miss_conf:.2%}")
    elif flag_saida == 0:
        print(f"{total_acessos} {taxa_hit:.2%} {taxa_miss_comp:.2%} {taxa_miss_cap:.2%} {taxa_miss_conf:.2%}")



def pretty_print_cache(cache_val, cache_tag):
    print("Cache:")
    for i in range(len(cache_val)):
        print("========== Linha ", i, "==========")
        for j in range(len(cache_val[i])):
            print("Bloco ", j, end=" ")
            print("Validade: ", cache_val[i][j], end=" ")
            print("Tag: ", cache_tag[i][j])
    return

def le_arquivo(arquivo, callback, n_bits_offset, n_bits_indice, cache_tag, cache_val, assoc, subst):
    print("Lendo arquivo")
    with open(arquivo, "rb") as arquivo_de_entrada:
        while True:
            endereco = arquivo_de_entrada.read(4)
            if not endereco:
                break
            endereco = int.from_bytes(endereco, byteorder="big")
            tag = endereco >> (n_bits_offset + n_bits_indice)  # Extrai a tag
            indice = (endereco >> n_bits_offset) & ((2**n_bits_indice) - 1)  # Extrai o indice

            #print(f"Endereço: {endereco}, Tag: {tag}, Índice: {indice}")
            callback(tag, indice, cache_tag, cache_val, assoc, subst)       # Chama a função de mapeamento
    print("Fim do arquivo")
    return


#Implementação politica sub LRU 
#ideia quando um bloco é acessado ele deve ser movido para o final da lista
#para fazer a substituição retirar o elemento que está mais a esquerda(primeiro item) da lista
#se der hit atualizar a ordem da lista
#se der miss verificar se é miss compulsorio ou de conflito / capacidade
def lru_cache_access(tag, indice, cache_tag, cache_val, assoc, subst):
    global hit, miss_comp, miss_conf

    found = False
    index_invalido = -1 #bloco invalido não encontrado

    # Verifica se o bloco está na cache
    for i in range(assoc):
        if cache_val[indice][i] == 1:  # Bloco válido
            if cache_tag[indice][i] == tag:  # Hit
                hit += 1
                # Move este bloco para o final da lista LRU
                subst[indice].remove(i)
                subst[indice].append(i)
                found = True #hit 
                break
        else:  # Bloco inválido
            if index_invalido == -1:
                index_invalido = i  # Armazena o primeiro índice inválido

    if found:
        return  # Função executada, sai da função

    # Se não houver hit, verifica blocos invalido
    if index_invalido != -1:
        cache_val[indice][index_invalido] = 1  # Define como válido
        cache_tag[indice][index_invalido] = tag  # Atualiza a tag
        subst[indice].append(index_invalido)  # Adiciona à lista LRU
        miss_comp += 1  # Miss compulsório
        return

    # Se todos os blocos são válidos, temos um miss de conflito ou capacidade
    miss_conf += 1  # Assume miss de conflito por padrão
    lru_index = subst[indice][0]  # Obtém o bloco menos recentemente usado
    cache_tag[indice][lru_index] = tag  # Substitui a tag
    # Remove o bloco LRU da lista e adiciona o novo bloco ao final
    subst[indice].remove(lru_index)
    subst[indice].append(lru_index)

#Implementação FIFO
#ideia quando um bloco é acessado verifica se ele está na lista e se estiver n mexer na ordem
#para fazer a substituição retirar o elemento que está mais a esquerda da lista
#se der hit não atualiza a ordem da lista
#se der miss verificar se é miss compulsorio ou de conflito / capacidade
def fifo_cache_access(tag, indice, cache_tag, cache_val, assoc, subst):
    global hit, miss_comp, miss_conf

    found = False
    index_invalido = -1

    # Verifica se o bloco está na cache
    for i in range(assoc):
        if cache_val[indice][i] == 1:  # Bloco válido
            if cache_tag[indice][i] == tag:  # Hit
                hit += 1
                found = True
                break
        else:  # Bloco inválido
            if index_invalido == -1:
                index_invalido = i

    if found:
        return

    # Se não houver hit, verifica blocos inválidos
    if index_invalido != -1:
        cache_val[indice][index_invalido] = 1
        cache_tag[indice][index_invalido] = tag
        subst[indice].append(index_invalido)
        miss_comp += 1
        return

    # Se todos os blocos são válidos, temos um miss de conflito ou capacidade
    miss_conf += 1
    fifo_index = subst[indice].pop(0)  # Remove o primeiro bloco da fila
    cache_tag[indice][fifo_index] = tag
    subst[indice].append(fifo_index)  # Adiciona o novo bloco ao final da fila



def mapeamentoDir(tag, indice, cache_tag, cache_val, assoc = 1, subst = None):
    global hit, miss_conf, miss_comp
    if cache_val[indice][0] == 0:
        miss_comp += 1                 # Miss compulsório
        cache_val[indice][0] = 1       # Atualiza o bit de validade
        cache_tag[indice][0] = tag     # Atualiza a tag
    elif cache_tag[indice][0] == tag:
        hit += 1                       # Hit  
    else:
        miss_conf += 1                 # Miss de conflito 
        cache_val[indice][0] = 1       # Atualiza o bit de validade
        cache_tag[indice][0] = tag     # Atualiza a tag
    return

def mapAssoc(tag, indice, cache_tag, cache_val, assoc, subst = None):
    if subst in ["l", "L"]:
        print("LRU")
    elif subst in ["f", "F"]:
        print("FIFO")
    elif subst in ["r", "R"]:
        print("Random")
    else:
        print("Politica de substituição invalida")

    return

def totalAssoc(tag, indice, cache_tag, cache_val, assoc, subst = None):
    return

if __name__ == "__main__":
    main()
    sys.exit(0)

