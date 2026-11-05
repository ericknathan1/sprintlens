import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsNotEmpty, IsString } from 'class-validator';

export class LoginDto {
  @ApiProperty({ example: 'admin@sprintlens.dev', description: 'E-mail cadastrado' })
  @IsEmail({}, { message: 'Forneça um e-mail válido' })
  @IsNotEmpty({ message: 'E-mail é obrigatório' })
  email: string;

  @ApiProperty({ example: 'Admin@123', description: 'Senha de acesso' })
  @IsString({ message: 'Senha deve ser um texto' })
  @IsNotEmpty({ message: 'Senha é obrigatória' })
  password: string;
}

