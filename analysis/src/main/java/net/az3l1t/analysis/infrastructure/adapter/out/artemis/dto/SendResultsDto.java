package net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.Map;

@Schema(description = "DTO для получения подтвержденного результата анализа из внешней системы (EMIAS)")
public record SendResultsDto(
        @Schema(description = "Идентификатор результата анализа", example = "507f1f77bcf86cd799439011")
        String id,
        
        @Schema(description = "ID пациента", example = "12345")
        Long patientId,
        
        @Schema(description = "ID врача", example = "67890")
        Long doctorId,
        
        @Schema(description = "Флаг подтверждения результата анализа (всегда true для внешних результатов)", example = "true")
        Boolean isConfirmed,
        
        @Schema(description = "Время проведения анализа", example = "2024-01-15T10:30:00")
        LocalDateTime analysisTime,
        
        @Schema(description = "Результаты анализов в виде Map", example = "{\"hb\": \"12.1\", \"rbc\": \"4.5\"}")
        Map<String, String> results
) {}