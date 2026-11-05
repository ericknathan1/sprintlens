import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsNotEmpty, IsString, MinLength } from 'class-validator';

export class RegisterDto {
  @ApiProperty({ example: 'Ana Silva', description: 'Nome completo do usuário' })
  @IsString({ message: 'Nome deve ser um texto' })
  @IsNotEmpty({ message: 'Nome é obrigatório' })
  name: string;

  @ApiProperty({ example: 'ana.silva@empresa.com', description: 'E-mail corporativo' })
  @IsEmail({}, { message: 'Forneça um e-mail válido' })
  @IsNotEmpty({ message: 'E-mail é obrigatório' })
  email: string;

  @ApiProperty({ example: 'SenhaForte@123', description: 'Senha de acesso (mínimo 6 caracteres)' })
  @IsString({ message: 'Senha deve ser um texto' })
  @MinLength(6, { message: 'A senha deve possuir no mínimo 6 caracteres' })
  password: string;
}

