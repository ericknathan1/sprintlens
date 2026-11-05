import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const logger = new Logger('SprintLensApiCore');
  const app = await NestFactory.create(AppModule);

  // Global Route Prefix
  app.setGlobalPrefix('api');

  // Input Validation & Transformation
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // CORS Configuration
  app.enableCors({
    origin: [
      process.env.CORS_ORIGIN || 'http://localhost:3000',
      'http://localhost:3000',
      'http://localhost:3001',
    ],
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    credentials: true,
  });

  // OpenAPI (Swagger) Documentation
  const swaggerConfig = new DocumentBuilder()
    .setTitle('SprintLens API Core')
    .setDescription('Orquestrador Backend e API Gateway da plataforma SprintLens')
    .setVersion('1.0.0')
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('api/docs', app, document);

  const port = process.env.API_PORT || process.env.PORT || 3001;
  await app.listen(port);

  logger.log(`🚀 SprintLens API Core running on: http://localhost:${port}/api`);
  logger.log(`📚 Swagger documentation available at: http://localhost:${port}/api/docs`);
}

bootstrap();

