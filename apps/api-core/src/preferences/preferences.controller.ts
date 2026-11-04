import { Controller, Get, Put, Body, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { PreferencesService } from './preferences.service';
import { UpdatePreferencesDto } from './dto/update-preferences.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@ApiTags('Preferences')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('preferences')
export class PreferencesController {
  constructor(private readonly preferencesService: PreferencesService) {}

  @Get()
  @ApiOperation({ summary: 'Obter preferências de cores do usuário atual' })
  @ApiResponse({ status: 200, description: 'Preferências retornadas com sucesso.' })
  async getPreferences(@CurrentUser('id') userId: string) {
    return this.preferencesService.getUserPreferences(userId);
  }

  @Put()
  @ApiOperation({ summary: 'Atualizar preferências de cores do usuário atual' })
  @ApiResponse({ status: 200, description: 'Preferências atualizadas com sucesso.' })
  async updatePreferences(
    @CurrentUser('id') userId: string,
    @Body() dto: UpdatePreferencesDto,
  ) {
    return this.preferencesService.updateUserPreferences(userId, dto);
  }
}

