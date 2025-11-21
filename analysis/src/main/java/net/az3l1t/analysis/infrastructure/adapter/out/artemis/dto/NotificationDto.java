package net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "DTO для уведомления о результатах анализов")
public class NotificationDto {
    
    @Schema(description = "ID результата анализа", example = "507f1f77bcf86cd799439011", required = true)
    private String analysisResultId;
    
    @Schema(description = "ID пациента", example = "12345", required = true)
    private Long patientId;
    
    @Schema(description = "ID врача", example = "67890", required = true)
    private Long doctorId;
    
    @Schema(description = "Тип уведомления", example = "RESULT_CONFIRMED", required = true)
    private NotificationType notificationType;
    
    @Schema(description = "Заголовок уведомления", example = "Результат анализа подтвержден", required = true)
    private String title;
    
    @Schema(description = "Текст уведомления", example = "Результат анализа №507f1f77bcf86cd799439011 был подтвержден врачом", required = true)
    private String message;
    
    @Schema(description = "Флаг подтверждения результата", example = "true")
    private Boolean isConfirmed;
    
    @Schema(description = "Время создания уведомления", example = "2024-01-15T10:30:00")
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime notificationTime;
    
    @Schema(description = "Время проведения анализа", example = "2024-01-15T09:00:00")
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime analysisTime;

    public enum NotificationType {
        RESULT_ADDED,
        RESULT_UPDATED,
        RESULT_CONFIRMED,
        RESULT_VIEWED,
    }
}

