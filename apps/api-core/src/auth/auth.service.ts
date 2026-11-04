import { Injectable, ConflictException, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { PrismaService } from '../prisma/prisma.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import * as bcrypt from 'bcrypt';
import { Role } from '@prisma/client';

@Injectable()
export class AuthService {
  constructor(
    private prisma: PrismaService,
    private jwtService: JwtService,
  ) {}

  async register(dto: RegisterDto) {
    const normalizedEmail = dto.email.trim().toLowerCase();

    const existingUser = await this.prisma.user.findUnique({
      where: { email: normalizedEmail },
    });

    if (existingUser) {
      throw new ConflictException('Já existe um usuário cadastrado com este e-mail.');
    }

    const hashedPassword = await bcrypt.hash(dto.password, 10);

    const user = await this.prisma.user.create({
      data: {
        name: dto.name.trim(),
        email: normalizedEmail,
        password: hashedPassword,
        role: Role.USER,
        isActive: true,
        preferences: {
          create: {
            primaryColor: '#537EED',
            secondaryColor: '#1E3A8A',
            alertColor: '#EF4444',
          },
        },
      },
      include: {
        preferences: true,
      },
    });

    const token = this.generateToken(user.id, user.email, user.role);

    return {
      token,
      user: this.sanitizeUser(user),
    };
  }

  async login(dto: LoginDto) {
    const normalizedEmail = dto.email.trim().toLowerCase();

    const user = await this.prisma.user.findUnique({
      where: { email: normalizedEmail },
      include: {
        preferences: true,
      },
    });

    if (!user) {
      throw new UnauthorizedException('Credenciais inválidas. Verifique seu e-mail e senha.');
    }

    const isPasswordValid = await bcrypt.compare(dto.password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Credenciais inválidas. Verifique seu e-mail e senha.');
    }

    if (!user.isActive) {
      throw new UnauthorizedException('Esta conta está inativa ou foi bloqueada pelo administrador.');
    }

    const token = this.generateToken(user.id, user.email, user.role);

    return {
      token,
      user: this.sanitizeUser(user),
    };
  }

  async getProfile(userId: string) {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      include: {
        preferences: true,
      },
    });

    if (!user) {
      throw new UnauthorizedException('Usuário não encontrado.');
    }

    return this.sanitizeUser(user);
  }

  private generateToken(userId: string, email: string, role: string): string {
    const payload = {
      sub: userId,
      email,
      role,
    };
    return this.jwtService.sign(payload);
  }

  private sanitizeUser(user: any) {
    const { password, ...safeUser } = user;
    return safeUser;
  }
}

