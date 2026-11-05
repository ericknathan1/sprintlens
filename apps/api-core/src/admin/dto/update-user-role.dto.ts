import { ApiProperty } from '@nestjs/swagger';
import { IsEnum, IsNotEmpty } from 'class-validator';
import { Role } from '@prisma/client';

export class UpdateUserRoleDto {
  @ApiProperty({ enum: Role, example: Role.ADMIN, description: 'Papel do usuário no sistema' })
  @IsEnum(Role, { message: 'Role deve ser ADMIN ou USER' })
  @IsNotEmpty({ message: 'Role é obrigatório' })
  role: Role;
}

