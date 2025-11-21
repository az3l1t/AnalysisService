package net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.Map;

@Data
@Schema(description = "DTO для создания нового результата анализа")
public class CreateInResultDto {
    
    @Schema(
            description = "ID пациента, для которого создается результат анализа",
            example = "12345",
            required = true
    )
    private Long patientId;
    
    @Schema(
            description = "ID врача, проводившего анализ",
            example = "67890",
            required = true
    )
    private Long doctorId;
    
    @Schema(
            description = "Флаг подтверждения результата анализа. По умолчанию false",
            example = "false",
            defaultValue = "false"
    )
    private Boolean isConfirmed;
    
    @Schema(
            description = """
                    Результаты анализов в виде Map, где:
                    - ключ - название анализа (например, "hb" для гемоглобина, "rbc" для эритроцитов)
                    - значение - результат анализа в виде строки
                    
                    **Пример:**
                    ```json
                    {
                      "hb": "12.1",
                      "rbc": "4.5",
                      "wbc": "6.8",
                      "platelets": "250"
                    }
                    ```
                    """,
            example = "{\"hb\": \"12.1\", \"rbc\": \"4.5\"}",
            required = true
    )
    private Map<String, String> results;
}