CREATE DATABASE IF NOT EXISTS olivia_db;

USE olivia_db;

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(150) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    data_nascimento DATE,
    email_verificado BOOLEAN DEFAULT FALSE,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE humor (
    id_humor INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    nivel_humor INT,
    observacao TEXT,
    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE conversa (
    id_conversa INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    data_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE mensagem (
    id_mensagem INT AUTO_INCREMENT PRIMARY KEY,
    id_conversa INT,
    remetente ENUM('usuario','olivia'),
    mensagem TEXT,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_conversa) REFERENCES conversa(id_conversa)
);


CREATE TABLE exercicio (
    id_exercicio INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100),
    descricao TEXT,
    categoria VARCHAR(50)
);


CREATE TABLE exercicio_realizado (
    id_realizacao INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_exercicio INT,
    data_realizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_exercicio) REFERENCES exercicio(id_exercicio)
);


CREATE TABLE avaliacao_ansiedade (
    id_avaliacao INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    nivel_ansiedade INT,
    observacao TEXT,
    data_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);




