package net.az3l1t.analysis.infrastructure.entity;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.Map;

@Document(collection = "analysis_result")
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class AnalysisResultDocument {
    @Id
    private String id;
    private Long patientId;
    private Long doctorId;
    @CreatedDate
    private LocalDateTime analysisTime;
    private Boolean isConfirmed;
    private Map<String, String> results;
}
