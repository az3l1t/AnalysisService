package net.az3l1t.analysis.domain.model;

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
public class AnalysisResult {
    @Id
    private String id;
    private Long patientId;
    private Long doctorId;
    @CreatedDate
    private LocalDateTime analysisTime;
    private Boolean isConfirmed;
    private Map<String, String> results;
}
