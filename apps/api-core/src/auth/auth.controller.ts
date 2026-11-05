import { Controller, Post, Body, Get, UseGuards, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { AuthService } from './auth.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import { Public } from './decorators/public.decorator';
import { CurrentUser } from './decorators/current-user.decorator';

@ApiTags('Auth')
@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Public()
  @Post('register')
  @ApiOperation({ summary: 'Autocadastro de novos usuários' })
  @ApiResponse({ status: 201, description: 'Usuário cadastrado com sucesso.' })
  @ApiResponse({ status: 409, description: 'E-mail já em uso.' })
  async register(@Body() dto: RegisterDto) {
    return this.authService.register(dto);
  }

  @Public()
  @Post('login')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Autenticação de usuário e emissão de JWT' })
  @ApiResponse({ status: 200, description: 'Login realizado com sucesso.' })
  @ApiResponse({ status: 401, description: 'Credenciais inválidas ou usuário inativo.' })
  async login(@Body() dto: LoginDto) {
    return this.authService.login(dto);
  }

  @UseGuards(JwtAuthGuard)
  @Get('me')
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Obter dados do usuário autenticado e preferências' })
  @ApiResponse({ status: 200, description: 'Dados do perfil obtidos com sucesso.' })
  @ApiResponse({ status: 401, description: 'Token JWT ausente ou expirado.' })
  async getProfile(@CurrentUser('id') userId: string) {
    return this.authService.getProfile(userId);
  }
}

