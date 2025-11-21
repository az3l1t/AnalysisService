package net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.Map;

@Data
@Schema(description = "DTO для получения обновленного результата анализа")
public class UpdateOutResultDto {
    
    @Schema(
            description = "Идентификатор обновленного результата анализа",
            example = "507f1f77bcf86cd799439011"
    )
    private String id;
    
    @Schema(
            description = "ID пациента (обновленное значение, если было изменено)",
            example = "12345"
    )
    private Long patientId;
    
    @Schema(
            description = "ID врача (обновленное значение, если было изменено)",
            example = "67890"
    )
    private Long doctorId;
    
    @Schema(
            description = "Флаг подтверждения результата анализа (обновленное значение, если было изменено)",
            example = "true"
    )
    private Boolean isConfirmed;
    
    @Schema(
            description = "Обновленные результаты анализов (полностью заменены, если были изменены)",
            example = "{\"hb\": \"13.4\", \"rbc\": \"4.8\"}"
    )
    private Map<String, String> results;
}