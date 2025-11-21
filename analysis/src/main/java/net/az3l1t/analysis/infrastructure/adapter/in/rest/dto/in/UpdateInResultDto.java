package net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.Map;

@Data
@Schema(description = "DTO для обновления существующего результата анализа")
public class UpdateInResultDto {
    
    @Schema(
            description = "ID результата анализа для обновления",
            example = "507f1f77bcf86cd799439011",
            required = true
    )
    private String id;
    
    @Schema(
            description = "ID пациента (опционально, обновляется только если указано)",
            example = "12345"
    )
    private Long patientId;
    
    @Schema(
            description = "ID врача (опционально, обновляется только если указано)",
            example = "67890"
    )
    private Long doctorId;
    
    @Schema(
            description = "Флаг подтверждения результата анализа (опционально)",
            example = "true"
    )
    private Boolean isConfirmed;
    
    @Schema(
            description = """
                    Обновленные результаты анализов (опционально).
                    Если указано, заменяет все существующие результаты.
                    Формат такой же, как в CreateInResultDto.
                    """,
            example = "{\"hb\": \"13.4\", \"rbc\": \"4.8\"}"
    )
    private Map<String, String> results;
}