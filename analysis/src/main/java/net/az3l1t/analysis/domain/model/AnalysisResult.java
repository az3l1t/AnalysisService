package net.az3l1t.analysis.domain.model;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;

import java.time.LocalDateTime;
import java.util.Map;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Schema(description = "Доменная модель результата анализа пациента")
public class AnalysisResult {
    
    @Id
    @Schema(description = "Уникальный идентификатор результата анализа", example = "507f1f77bcf86cd799439011")
    private String id;
    
    @Schema(description = "ID пациента, для которого был проведен анализ", example = "12345", required = true)
    private Long patientId;
    
    @Schema(description = "ID врача, проводившего анализ", example = "67890", required = true)
    private Long doctorId;
    
    @CreatedDate
    @Schema(description = "Дата и время создания результата анализа. Автоматически устанавливается при создании", 
            example = "2024-01-15T10:30:00")
    private LocalDateTime analysisTime;
    
    @Schema(description = "Флаг подтверждения результата анализа. False - не подтвержден, True - подтвержден", 
            example = "false", defaultValue = "false")
    private Boolean isConfirmed;
    
    @Schema(description = """
            Результаты анализов в виде Map, где:
            - ключ - название анализа (например, "hb" для гемоглобина)
            - значение - результат анализа в виде строки
            
            Примеры ключей:
            - "hb" - гемоглобин
            - "rbc" - эритроциты
            - "wbc" - лейкоциты
            - "platelets" - тромбоциты
            """, 
            example = "{\"hb\": \"12.1\", \"rbc\": \"4.5\", \"wbc\": \"6.8\"}",
            required = true)
    private Map<String, String> results;
}
