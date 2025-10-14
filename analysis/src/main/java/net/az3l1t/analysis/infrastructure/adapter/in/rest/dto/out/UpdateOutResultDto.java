package net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out;

import lombok.Data;

import java.util.Map;

@Data
public class UpdateOutResultDto {
    private String id;
    private Long patientId;
    private Long doctorId;
    private Boolean isConfirmed;
    private Map<String, String> results;
}