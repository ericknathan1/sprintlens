import { PrismaClient, Role } from '@prisma/client';
import * as bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Starting database seeding...');

  const adminEmail = 'admin@sprintlens.dev';
  const rawPassword = 'Admin@123';
  const hashedPassword = await bcrypt.hash(rawPassword, 10);

  const adminUser = await prisma.user.upsert({
    where: { email: adminEmail },
    update: {
      role: Role.ADMIN,
      isActive: true,
      password: hashedPassword,
    },
    create: {
      email: adminEmail,
      name: 'SprintLens Admin',
      password: hashedPassword,
      role: Role.ADMIN,
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

  // Ensure preferences exist if user already existed
  if (!adminUser.preferences) {
    await prisma.userPreferences.create({
      data: {
        userId: adminUser.id,
        primaryColor: '#537EED',
        secondaryColor: '#1E3A8A',
        alertColor: '#EF4444',
      },
    });
  }

  console.log(`✅ Default Admin user ensured: ${adminEmail}`);
  console.log(`   Role: ${adminUser.role}`);
  console.log(`   ID: ${adminUser.id}`);
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

