import {
  Controller,
  Get,
  Patch,
  Post,
  Delete,
  Param,
  Body,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { AdminService } from './admin.service';
import { UpdateUserStatusDto } from './dto/update-user-status.dto';
import { UpdateUserRoleDto } from './dto/update-user-role.dto';
import { ResetPasswordDto } from './dto/reset-password.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../auth/guards/roles.guard';
import { Roles } from '../auth/decorators/roles.decorator';
import { CurrentUser } from '../auth/decorators/current-user.decorator';
import { Role } from '@prisma/client';

@ApiTags('Admin')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles(Role.ADMIN)
@Controller('admin')
export class AdminController {
  constructor(private readonly adminService: AdminService) {}

  @Get('metrics')
  @ApiOperation({ summary: 'Obter métricas globais de uso da plataforma (Admin)' })
  @ApiResponse({ status: 200, description: 'Métricas retornadas com sucesso.' })
  async getMetrics() {
    return this.adminService.getPlatformMetrics();
  }

  @Get('users')
  @ApiOperation({ summary: 'Listar todos os usuários cadastrados e projetos (Admin)' })
  @ApiResponse({ status: 200, description: 'Lista de usuários retornada com sucesso.' })
  async listUsers() {
    return this.adminService.listUsers();
  }

  @Patch('users/:id/status')
  @ApiOperation({ summary: 'Ativar ou bloquear conta de usuário (Admin)' })
  @ApiResponse({ status: 200, description: 'Status do usuário atualizado.' })
  async setUserStatus(
    @Param('id') targetUserId: string,
    @CurrentUser('id') currentAdminId: string,
    @Body() dto: UpdateUserStatusDto,
  ) {
    return this.adminService.setUserStatus(targetUserId, currentAdminId, dto.isActive);
  }

  @Patch('users/:id/role')
  @ApiOperation({ summary: 'Promover ou rebaixar papel do usuário (ADMIN / USER)' })
  @ApiResponse({ status: 200, description: 'Papel do usuário atualizado.' })
  async setUserRole(
    @Param('id') targetUserId: string,
    @CurrentUser('id') currentAdminId: string,
    @Body() dto: UpdateUserRoleDto,
  ) {
    return this.adminService.setUserRole(targetUserId, currentAdminId, dto.role);
  }

  @Post('users/:id/reset-password')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Resetar a senha de um usuário (Admin)' })
  @ApiResponse({ status: 200, description: 'Senha redefinida com sucesso.' })
  async resetPassword(
    @Param('id') targetUserId: string,
    @Body() dto: ResetPasswordDto,
  ) {
    return this.adminService.resetUserPassword(targetUserId, dto.newPassword);
  }

  @Delete('users/:id')
  @ApiOperation({ summary: 'Excluir definitivamente um usuário (Admin)' })
  @ApiResponse({ status: 200, description: 'Usuário excluído com sucesso.' })
  async deleteUser(
    @Param('id') targetUserId: string,
    @CurrentUser('id') currentAdminId: string,
  ) {
    return this.adminService.deleteUser(targetUserId, currentAdminId);
  }
}

