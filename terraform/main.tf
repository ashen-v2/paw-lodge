
resource "aws_instance" "app_instance" {
  ami           = var.app_ami
  instance_type = var.app_instance_type
  subnet_id     = aws_subnet.public_subnet_1.id
  security_groups = [aws_security_group.app_sg.name]

  tags = var.global_tag
}


resource "aws_vpc" "paw_lodge_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    "Name" = "paw_lodge_vpc"
    "Project" = var.global_tag["Project"]
  }
  
}

resource "aws_subnet" "public_subnet_1" {
  vpc_id            = aws_vpc.paw_lodge_vpc.id
  cidr_block        = "10.0.1.0/28"
  availability_zone = var.availability_zones[0]

  tags = var.global_tag
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id            = aws_vpc.paw_lodge_vpc.id
  cidr_block        = "10.0.2.0/28"
  availability_zone = var.availability_zones[1]

  tags = var.global_tag
}

resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.paw_lodge_vpc.id
  cidr_block        = "10.0.11.0/28"
  availability_zone = var.availability_zones[0]

  tags = var.global_tag
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.paw_lodge_vpc.id
  cidr_block        = "10.0.12.0/28"
  availability_zone = var.availability_zones[1]

  tags = var.global_tag
}

resource "aws_security_group" "app_sg" {
    name = "app_sg"
    vpc_id = aws_vpc.paw_lodge_vpc.id

    egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = var.global_tag
}

resource "aws_security_group" "db_sg" {
    name = "db_sg"
    vpc_id = aws_vpc.paw_lodge_vpc.id

    egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = var.global_tag
}

resource "aws_vpc_security_group_ingress_rule" "allow_http_inbound" {
    security_group_id = aws_security_group.app_sg.id
    cidr_ipv4 = "0.0.0.0/0"
    from_port = 80
    to_port = 80
    ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "allow_db_inbound"{
    security_group_id = aws_security_group.db_sg.id
    from_port = 5432
    to_port = 5432
    ip_protocol = "tcp"
    referenced_security_group_id = aws_security_group.app_sg.id
}

resource "aws_vpc_security_group_egress_rule" "allow_db_outbound"{
    security_group_id = aws_security_group.app_sg.id
    from_port = 5432
    to_port = 5432
    ip_protocol = "tcp"
    referenced_security_group_id = aws_security_group.db_sg.id
}

resource "aws_internet_gateway" "paw_lodge_igw" {
  vpc_id = aws_vpc.paw_lodge_vpc.id

  tags = var.global_tag
}

resource "aws_route_table" "public_route_table"{
  vpc_id = aws_vpc.paw_lodge_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.paw_lodge_igw.id
  }

}

resource "aws_route_table_association" "public_subnet_1_association" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table_association" "public_subnet_2_association" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table" "private_route_table"{
  vpc_id = aws_vpc.paw_lodge_vpc.id
}

resource "aws_route_table_association" "private_subnet_1_association" {
  subnet_id      = aws_subnet.private_subnet_1.id
  route_table_id = aws_route_table.private_route_table.id
}

resource "aws_route_table_association" "private_subnet_2_association" {
  subnet_id      = aws_subnet.private_subnet_2.id
  route_table_id = aws_route_table.private_route_table.id
}




    