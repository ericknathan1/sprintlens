import { Injectable, BadRequestException, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { Role } from '@prisma/client';
import * as bcrypt from 'bcrypt';
import * as crypto from 'crypto';

@Injectable()
export class AdminService {
  constructor(private prisma: PrismaService) {}

  async getPlatformMetrics() {
    const [totalUsers, activeUsers, totalProjects, totalIssuesProcessed, latestProject, latestIssue] =
      await Promise.all([
        this.prisma.user.count(),
        this.prisma.user.count({ where: { isActive: true } }),
        this.prisma.project.count(),
        this.prisma.jiraIssue.count(),
        this.prisma.project.findFirst({
          orderBy: { updatedAt: 'desc' },
          select: { updatedAt: true },
        }),
        this.prisma.jiraIssue.findFirst({
          orderBy: { createdAt: 'desc' },
          select: { createdAt: true },
        }),
      ]);

    const lastUploadDates = [latestProject?.updatedAt, latestIssue?.createdAt].filter(Boolean) as Date[];
    const lastGlobalActivityDate =
      lastUploadDates.length > 0
        ? new Date(Math.max(...lastUploadDates.map((d) => d.getTime())))
        : null;

    return {
      totalUsers,
      activeUsers,
      totalProjects,
      totalIssuesProcessed,
      lastGlobalActivityDate,
    };
  }

  async listUsers() {
    const users = await this.prisma.user.findMany({
      orderBy: { createdAt: 'desc' },
      select: {
        id: true,
        name: true,
        email: true,
        role: true,
        isActive: true,
        createdAt: true,
        updatedAt: true,
        preferences: true,
        _count: {
          select: {
            projects: true,
          },
        },
      },
    });

    return users;
  }

  async setUserStatus(targetUserId: string, currentAdminId: string, isActive: boolean) {
    if (targetUserId === currentAdminId && !isActive) {
      throw new BadRequestException('Você não pode desativar sua própria conta de administrador.');
    }

    const targetUser = await this.prisma.user.findUnique({
      where: { id: targetUserId },
    });

    if (!targetUser) {
      throw new NotFoundException('Usuário não encontrado.');
    }

    return this.prisma.user.update({
      where: { id: targetUserId },
      data: { isActive },
      select: {
        id: true,
        name: true,
        email: true,
        role: true,
        isActive: true,
        updatedAt: true,
      },
    });
  }

  async setUserRole(targetUserId: string, currentAdminId: string, role: Role) {
    if (targetUserId === currentAdminId && role !== Role.ADMIN) {
      throw new BadRequestException('Você não pode remover seus próprios privilégios de administrador.');
    }

    const targetUser = await this.prisma.user.findUnique({
      where: { id: targetUserId },
    });

    if (!targetUser) {
      throw new NotFoundException('Usuário não encontrado.');
    }

    return this.prisma.user.update({
      where: { id: targetUserId },
      data: { role },
      select: {
        id: true,
        name: true,
        email: true,
        role: true,
        isActive: true,
        updatedAt: true,
      },
    });
  }

  async resetUserPassword(targetUserId: string, newPassword?: string) {
    const targetUser = await this.prisma.user.findUnique({
      where: { id: targetUserId },
    });

    if (!targetUser) {
      throw new NotFoundException('Usuário não encontrado.');
    }

    const generatedPassword = newPassword || `Sprint@${crypto.randomBytes(4).toString('hex')}!`;
    const hashedPassword = await bcrypt.hash(generatedPassword, 10);

    await this.prisma.user.update({
      where: { id: targetUserId },
      data: { password: hashedPassword },
    });

    return {
      message: 'Senha redefinida com sucesso.',
      userId: targetUserId,
      temporaryPassword: newPassword ? undefined : generatedPassword,
    };
  }

  async deleteUser(targetUserId: string, currentAdminId: string) {
    if (targetUserId === currentAdminId) {
      throw new BadRequestException('Você não pode excluir sua própria conta.');
    }

    const targetUser = await this.prisma.user.findUnique({
      where: { id: targetUserId },
    });

    if (!targetUser) {
      throw new NotFoundException('Usuário não encontrado.');
    }

    await this.prisma.user.delete({
      where: { id: targetUserId },
    });

    return {
      message: `Usuário ${targetUser.email} removido com sucesso.`,
    };
  }
}

