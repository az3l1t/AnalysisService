package net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto;

import java.time.LocalDateTime;
import java.util.Map;

public record SendResultsDto(
        String id,
        Long patientId,
        Long doctorId,
        Boolean isConfirmed,
        LocalDateTime analysisTime,
        Map<String, String>results
) {}