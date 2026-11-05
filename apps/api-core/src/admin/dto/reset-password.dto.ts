import { ApiPropertyOptional } from '@nestjs/swagger';
import { IsOptional, IsString, MinLength } from 'class-validator';

export class ResetPasswordDto {
  @ApiPropertyOptional({ example: 'NovaSenha@2026', description: 'Nova senha (mínimo 6 caracteres). Se omitida, uma será gerada automaticamente.' })
  @IsOptional()
  @IsString({ message: 'Senha deve ser texto' })
  @MinLength(6, { message: 'Senha deve possuir pelo menos 6 caracteres' })
  newPassword?: string;
}

