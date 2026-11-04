import {
  Controller,
  Get,
  Post,
  Delete,
  Param,
  Body,
  UseGuards,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { ProjectsService } from './projects.service';
import { CreateProjectDto } from './dto/create-project.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';
import { Role } from '@prisma/client';

@ApiTags('Projects')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('projects')
export class ProjectsController {
  constructor(private readonly projectsService: ProjectsService) {}

  @Post()
  @ApiOperation({ summary: 'Criar um novo projeto para armazenar dados de sprints' })
  @ApiResponse({ status: 201, description: 'Projeto criado com sucesso.' })
  async create(
    @CurrentUser('id') userId: string,
    @Body() dto: CreateProjectDto,
  ) {
    return this.projectsService.create(userId, dto);
  }

  @Get()
  @ApiOperation({ summary: 'Listar projetos pertencentes ao usuário (ou todos se Admin)' })
  @ApiResponse({ status: 200, description: 'Lista de projetos retornada com sucesso.' })
  async findAll(
    @CurrentUser('id') userId: string,
    @CurrentUser('role') role: Role,
  ) {
    return this.projectsService.findAll(userId, role);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Obter detalhes de um projeto específico' })
  @ApiResponse({ status: 200, description: 'Projeto encontrado.' })
  @ApiResponse({ status: 404, description: 'Projeto não encontrado.' })
  async findOne(
    @Param('id') id: string,
    @CurrentUser('id') userId: string,
    @CurrentUser('role') role: Role,
  ) {
    return this.projectsService.findOne(id, userId, role);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Excluir um projeto e seus registros' })
  @ApiResponse({ status: 200, description: 'Projeto excluído com sucesso.' })
  async remove(
    @Param('id') id: string,
    @CurrentUser('id') userId: string,
    @CurrentUser('role') role: Role,
  ) {
    return this.projectsService.remove(id, userId, role);
  }
}

