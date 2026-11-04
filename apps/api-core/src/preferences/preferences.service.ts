import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { UpdatePreferencesDto } from './dto/update-preferences.dto';

@Injectable()
export class PreferencesService {
  constructor(private prisma: PrismaService) {}

  async getUserPreferences(userId: string) {
    let preferences = await this.prisma.userPreferences.findUnique({
      where: { userId },
    });

    if (!preferences) {
      preferences = await this.prisma.userPreferences.create({
        data: {
          userId,
          primaryColor: '#537EED',
          secondaryColor: '#1E3A8A',
          alertColor: '#EF4444',
        },
      });
    }

    return preferences;
  }

  async updateUserPreferences(userId: string, dto: UpdatePreferencesDto) {
    const preferences = await this.prisma.userPreferences.upsert({
      where: { userId },
      update: {
        ...(dto.primaryColor && { primaryColor: dto.primaryColor }),
        ...(dto.secondaryColor && { secondaryColor: dto.secondaryColor }),
        ...(dto.alertColor && { alertColor: dto.alertColor }),
      },
      create: {
        userId,
        primaryColor: dto.primaryColor || '#537EED',
        secondaryColor: dto.secondaryColor || '#1E3A8A',
        alertColor: dto.alertColor || '#EF4444',
      },
    });

    return preferences;
  }
}

