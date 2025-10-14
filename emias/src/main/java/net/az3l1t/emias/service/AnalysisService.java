package net.az3l1t.emias.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.az3l1t.emias.dto.SendResultDto;
import net.az3l1t.emias.repository.AnalysisRepository;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnalysisService {
    private final AnalysisRepository analysisRepository;
    private final ObjectMapper objectMapper;

    public SendResultDto getById(String id) {
        try {
            String json = analysisRepository.get("analysis:" + id);
            log.info("Got json from external service: " + json);
            if (json == null) return null;
            return objectMapper.readValue(json, SendResultDto.class);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            return null;
        }
    }
}
