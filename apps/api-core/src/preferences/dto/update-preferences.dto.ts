import { ApiPropertyOptional } from '@nestjs/swagger';
import { IsOptional, IsString, Matches } from 'class-validator';

const HEX_COLOR_REGEX = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;

export class UpdatePreferencesDto {
  @ApiPropertyOptional({ example: '#537EED', description: 'Cor Principal de Destaque (Hex)' })
  @IsOptional()
  @IsString()
  @Matches(HEX_COLOR_REGEX, { message: 'Cor primária deve ser um código hexadecimal válido (ex: #537EED)' })
  primaryColor?: string;

  @ApiPropertyOptional({ example: '#1E3A8A', description: 'Cor Secundária de Contexto (Hex)' })
  @IsOptional()
  @IsString()
  @Matches(HEX_COLOR_REGEX, { message: 'Cor secundária deve ser um código hexadecimal válido (ex: #1E3A8A)' })
  secondaryColor?: string;

  @ApiPropertyOptional({ example: '#EF4444', description: 'Cor de Alerta / Bugs (Hex)' })
  @IsOptional()
  @IsString()
  @Matches(HEX_COLOR_REGEX, { message: 'Cor de alerta deve ser um código hexadecimal válido (ex: #EF4444)' })
  alertColor?: string;
}

