import { Injectable, NotFoundException, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateProjectDto } from './dto/create-project.dto';
import { Role } from '@prisma/client';

@Injectable()
export class ProjectsService {
  constructor(private prisma: PrismaService) {}

  async create(userId: string, dto: CreateProjectDto) {
    return this.prisma.project.create({
      data: {
        name: dto.name.trim(),
        description: dto.description?.trim(),
        userId,
      },
      include: {
        _count: {
          select: { issues: true },
        },
      },
    });
  }

  async findAll(userId: string, role: Role) {
    const where = role === Role.ADMIN ? {} : { userId };

    return this.prisma.project.findMany({
      where,
      orderBy: { updatedAt: 'desc' },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
        _count: {
          select: { issues: true },
        },
      },
    });
  }

  async findOne(id: string, userId: string, role: Role) {
    const project = await this.prisma.project.findUnique({
      where: { id },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
        _count: {
          select: { issues: true },
        },
      },
    });

    if (!project) {
      throw new NotFoundException('Projeto não encontrado.');
    }

    if (role !== Role.ADMIN && project.userId !== userId) {
      throw new ForbiddenException('Acesso negado a este projeto.');
    }

    return project;
  }

  async remove(id: string, userId: string, role: Role) {
    await this.findOne(id, userId, role);

    await this.prisma.project.delete({
      where: { id },
    });

    return { message: 'Projeto e dados associados excluídos com sucesso.' };
  }
}

