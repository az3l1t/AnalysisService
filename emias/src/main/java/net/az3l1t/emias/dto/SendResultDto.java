package net.az3l1t.emias.dto;

import java.time.LocalDateTime;
import java.util.Map;

public record SendResultDto(
        String id,
        Long patientId,
        Long doctorId,
        Boolean isConfirmed,
        LocalDateTime analysisTime,
        Map<String, String> results
) {}
