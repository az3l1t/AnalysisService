package net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.Map;

@Data
@Schema(description = "DTO для получения результата анализа после создания")
public class GetOutResultDto {
    
    @Schema(
            description = "Уникальный идентификатор созданного результата анализа",
            example = "507f1f77bcf86cd799439011"
    )
    private String id;
    
    @Schema(
            description = "ID пациента, для которого создан результат анализа",
            example = "12345"
    )
    private Long patientId;
    
    @Schema(
            description = "ID врача, проводившего анализ",
            example = "67890"
    )
    private Long doctorId;
    
    @Schema(
            description = "Флаг подтверждения результата анализа",
            example = "false"
    )
    private Boolean isConfirmed;
    
    @Schema(
            description = "Результаты анализов в виде Map (ключ - название анализа, значение - результат)",
            example = "{\"hb\": \"12.1\", \"rbc\": \"4.5\"}"
    )
    private Map<String, String> results;
}