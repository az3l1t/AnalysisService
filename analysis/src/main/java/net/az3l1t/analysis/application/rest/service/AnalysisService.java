package net.az3l1t.analysis.application.rest.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.az3l1t.analysis.application.rest.client.EmiasClient;
import net.az3l1t.analysis.application.rest.mapper.AnalysisServiceMapper;
import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.domain.port.in.AnalysisResultUseCase;
import net.az3l1t.analysis.domain.port.out.AnalysisResultPort;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.CreateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.UpdateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnalysisService implements AnalysisResultUseCase {
    private final AnalysisResultPort resultPort;
    private final AnalysisServiceMapper analysisServiceMapper;
    private final EmiasClient emiasClient;

    @Override
    @Transactional
    public AnalysisResult create(CreateInResultDto createInResultDto) {
        AnalysisResult savedResult = resultPort.save(
                analysisServiceMapper.toAnalysisResult(createInResultDto)
        );
        log.info("Created AnalysisResult: {}", savedResult);
        return savedResult;
    }

    @Override
    @Transactional
    public AnalysisResult update(UpdateInResultDto updateInResultDto) {
        AnalysisResult existingResult = resultPort.findById(updateInResultDto.getId());
        analysisServiceMapper.mergeAnalysisResult(updateInResultDto, existingResult);
        log.info("Updated AnalysisResult: {}", existingResult);
        return resultPort.save(existingResult);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<AnalysisResult> getById(String id) {
        return resultPort.findByIdOptional(id);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<AnalysisResult> getAll(int page, int size) {
        return resultPort.findAll(page, size);
    }

    @Override
    @Transactional(readOnly = true)
    public void delete(String id) {
        log.info("Deleting AnalysisResult: {}", id);
        resultPort.deleteById(id);
    }

    @Override
    @Transactional
    public void confirmAnalysisResult(String id) {
        AnalysisResult analysisResult = resultPort.findById(id);
        analysisResult.setIsConfirmed(true);
        resultPort.save(analysisResult);
        log.info("Confirmed AnalysisResult: {}", analysisResult);
    }

    @Override
    public SendResultsDto getConfirmedResults(String id) {
        return emiasClient.getResultById(id);
    }
}
