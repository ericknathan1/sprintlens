import { ApiProperty } from '@nestjs/swagger';
import { IsBoolean, IsNotEmpty } from 'class-validator';

export class UpdateUserStatusDto {
  @ApiProperty({ example: true, description: 'Status de ativação da conta (true: ativo, false: bloqueado)' })
  @IsBoolean({ message: 'isActive deve ser um booleano' })
  @IsNotEmpty({ message: 'isActive é obrigatório' })
  isActive: boolean;
}

