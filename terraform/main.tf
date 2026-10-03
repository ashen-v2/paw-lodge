
data "aws_ssm_parameter" "al2023_ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

resource "aws_iam_role" "instance_role" {
  name = "pawlodge-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.global_tag
}

resource "aws_iam_role_policy_attachment" "instance_ssm" {
  role       = aws_iam_role.instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "instance_role" {
  name = "pawlodge-instance-role"
  role = aws_iam_role.instance_role.name

  tags = var.global_tag
}

resource "aws_instance" "app_instance" {
  ami                         = data.aws_ssm_parameter.al2023_ami.value
  instance_type               = var.app_instance_type
  subnet_id                   = aws_subnet.public_subnet_1.id
  vpc_security_group_ids      = [aws_security_group.app_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.instance_role.name
  associate_public_ip_address = true
  user_data_replace_on_change = true

  user_data = file("${path.module}/cloud-config.yml")

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  tags = merge(var.global_tag, {
    Name = "pawlodge-app"
  })
}


resource "aws_vpc" "paw_lodge_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    "Name"    = "paw_lodge_vpc"
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
  name   = "app_sg"
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
  name   = "db_sg"
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
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "allow_https_inbound" {
  security_group_id = aws_security_group.app_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "allow_db_inbound" {
  security_group_id            = aws_security_group.db_sg.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.app_sg.id
}

resource "aws_vpc_security_group_ingress_rule" "allow_db_from_public_subnet_1" {
  security_group_id = aws_security_group.db_sg.id
  from_port         = 5432
  to_port           = 5432
  ip_protocol       = "tcp"
  cidr_ipv4         = aws_subnet.public_subnet_1.cidr_block
}

resource "aws_vpc_security_group_egress_rule" "allow_db_outbound" {
  security_group_id            = aws_security_group.app_sg.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.db_sg.id
}

resource "aws_internet_gateway" "paw_lodge_igw" {
  vpc_id = aws_vpc.paw_lodge_vpc.id

  tags = var.global_tag
}

resource "aws_route_table" "public_route_table" {
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

resource "aws_route_table" "private_route_table" {
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

resource "aws_db_subnet_group" "sandbox_db" {
  name       = "pawlodge-sandbox-db"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]

  tags = merge(var.global_tag, {
    Name = "pawlodge-sandbox-db"
  })
}

resource "aws_db_instance" "sandbox_postgres" {
  identifier     = "pawlodge-sandbox-postgres"
  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class

  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.sandbox_db.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  publicly_accessible    = false
  multi_az               = false

  backup_retention_period = 0
  skip_final_snapshot     = true
  deletion_protection     = false
  apply_immediately       = true

  tags = merge(var.global_tag, {
    Name        = "pawlodge-sandbox-postgres"
    Environment = "sandbox"
  })
}






    