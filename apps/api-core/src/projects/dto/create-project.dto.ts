import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { IsNotEmpty, IsOptional, IsString, MaxLength } from 'class-validator';

export class CreateProjectDto {
  @ApiProperty({ example: 'Squad FinTech Alpha', description: 'Nome do Projeto ou Equipe' })
  @IsString({ message: 'Nome deve ser um texto' })
  @IsNotEmpty({ message: 'Nome do projeto é obrigatório' })
  @MaxLength(100, { message: 'Nome do projeto não pode ter mais de 100 caracteres' })
  name: string;

  @ApiPropertyOptional({ example: 'Métricas de fluxo e sustentação do time de pagamentos', description: 'Descrição opcional' })
  @IsOptional()
  @IsString({ message: 'Descrição deve ser um texto' })
  @MaxLength(255, { message: 'Descrição não pode ter mais de 255 caracteres' })
  description?: string;
}

