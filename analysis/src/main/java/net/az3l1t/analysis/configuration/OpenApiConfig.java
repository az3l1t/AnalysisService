package net.az3l1t.analysis.configuration;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI analysisServiceOpenAPI() {
        final String securitySchemeName = "bearerAuth";
        return new OpenAPI()
                .info(new Info()
                        .title("Analysis Service API")
                        .description("""
                                API для управления результатами анализов.
                                
                                Сервис предоставляет функциональность для:
                                - Создания и управления результатами анализов пациентов
                                - Подтверждения результатов анализов
                                - Получения подтвержденных результатов из внешних систем
                                - Получения списка результатов с пагинацией
                                
                                Все endpoints требуют JWT аутентификации.
                                """)
                        .version("v1.0")
                        .contact(new Contact()
                                .name("Analysis Service Team")
                                .email("support@analysis.service"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0.html")))
                .addSecurityItem(new SecurityRequirement()
                        .addList(securitySchemeName))
                .components(new Components()
                        .addSecuritySchemes(securitySchemeName,
                                new SecurityScheme()
                                        .name(securitySchemeName)
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")
                                        .description("JWT токен для аутентификации. Формат: Bearer {token}")));
    }
}

