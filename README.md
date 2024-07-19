# Sprint4 - MVP Microsserviços - PUC Trading Bank (Bank service)
Pós Graduação em Engenharia de Software - PUC-Rio - MVP Sprint 4

Este projeto é um MVP de um microsserviço de um Banco virtual. Este serviço, em conjunto com os outros dois microsserviços de User e Transaction, implementam um sistema básico de banco, onde é possível criar e excluir usuários, fazer depósitos e saques fictícios, e enviar dinheiro para outro usuário.

O objetivo do projeto é por em prática o que foi aprendido na Sprint 4 do curso, além de começar um portfólio de apresentação profissional.

---
## Como executar 

Primeiramente, é necessário ter o Docker instalado na sua máquina.

Após realizar o clone deste projeto no git, abra um terminal na pasta do projeto. Digite o seguinte comando como administrador:

```
$ sudo docker build -t bank_service .
```

Este comando criará a imagem da máquina onde o microsserviço rodará.

Em seguida, após as configurações realizadas automaticamente, basta rodar o seguinte comando:

```
$ docker run -p 5000:5000 bank_service
```

O microsserviço, portanto, estará pronto para ser utilizado, acessando o seguinte link no seu navegador:

```
http://127.0.0.1:5000/
```

Neste link, você poderá interagir com as rotas implementadas.