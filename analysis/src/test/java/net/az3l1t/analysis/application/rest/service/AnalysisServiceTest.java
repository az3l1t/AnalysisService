package net.az3l1t.analysis.application.rest.service;

import net.az3l1t.analysis.application.rest.client.EmiasClient;
import net.az3l1t.analysis.application.rest.mapper.AnalysisServiceMapper;
import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.domain.port.out.AnalysisResultPort;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.CreateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.UpdateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AnalysisServiceTest {

    @Mock
    private AnalysisResultPort analysisResultPort;
    @Mock
    private AnalysisServiceMapper analysisServiceMapper;
    @Mock
    private EmiasClient emiasClient;

    @InjectMocks
    private AnalysisService analysisService;

    private AnalysisResult domainResult;

    @BeforeEach
    void setUp() {
        domainResult = new AnalysisResult("id-1", 1L, 2L, LocalDateTime.now(), false, Map.of("hb", "12"));
    }

    @Test
    void shouldCreateAnalysisResult() {
        CreateInResultDto dto = new CreateInResultDto();
        dto.setPatientId(1L);
        dto.setDoctorId(2L);
        dto.setIsConfirmed(false);
        dto.setResults(Map.of("hb", "12"));

        when(analysisServiceMapper.toAnalysisResult(dto)).thenReturn(domainResult);
        when(analysisResultPort.save(domainResult)).thenReturn(domainResult);

        AnalysisResult saved = analysisService.create(dto);

        assertThat(saved).isEqualTo(domainResult);
        verify(analysisResultPort).save(domainResult);
        verify(analysisServiceMapper).toAnalysisResult(dto);
    }

    @Test
    void shouldUpdateExistingResult() {
        UpdateInResultDto dto = new UpdateInResultDto();
        dto.setId("id-1");
        dto.setResults(Map.of("hb", "14"));

        when(analysisResultPort.findById("id-1")).thenReturn(domainResult);
        when(analysisResultPort.save(domainResult)).thenReturn(domainResult);

        AnalysisResult updated = analysisService.update(dto);

        assertThat(updated).isEqualTo(domainResult);
        verify(analysisServiceMapper).mergeAnalysisResult(dto, domainResult);
        verify(analysisResultPort).save(domainResult);
    }

    @Test
    void shouldThrowWhenResultNotFoundOnUpdate() {
        UpdateInResultDto dto = new UpdateInResultDto();
        dto.setId("missing");
        when(analysisResultPort.findById("missing")).thenThrow(new RuntimeException("No result found"));

        assertThatThrownBy(() -> analysisService.update(dto))
                .isInstanceOf(RuntimeException.class);
    }

    @Test
    void shouldReturnOptionalResult() {
        when(analysisResultPort.findByIdOptional("id-1")).thenReturn(Optional.of(domainResult));

        Optional<AnalysisResult> result = analysisService.getById("id-1");

        assertThat(result).contains(domainResult);
    }

    @Test
    void shouldReturnPagedResults() {
        Page<AnalysisResult> page = new PageImpl<>(List.of(domainResult));
        when(analysisResultPort.findAll(0, 10)).thenReturn(page);

        Page<AnalysisResult> actual = analysisService.getAll(0, 10);

        assertThat(actual.getContent()).hasSize(1);
        verify(analysisResultPort).findAll(0, 10);
    }

    @Test
    void shouldDeleteById() {
        analysisService.delete("id-1");
        verify(analysisResultPort).deleteById("id-1");
    }

    @Test
    void shouldConfirmResult() {
        AnalysisResult unconfirmed = new AnalysisResult("id-1", 1L, 2L, LocalDateTime.now(), false, Map.of());
        when(analysisResultPort.findById("id-1")).thenReturn(unconfirmed);
        when(analysisResultPort.save(unconfirmed)).thenReturn(unconfirmed);

        analysisService.confirmAnalysisResult("id-1");

        assertThat(unconfirmed.getIsConfirmed()).isTrue();
        verify(analysisResultPort).save(unconfirmed);
    }

    @Test
    void shouldGetConfirmedResultsFromExternalService() {
        SendResultsDto dto = new SendResultsDto("id-1", 1L, 2L, true, LocalDateTime.now(), Map.of());
        when(emiasClient.getResultById("id-1")).thenReturn(dto);

        SendResultsDto actual = analysisService.getConfirmedResults("id-1");

        assertThat(actual).isEqualTo(dto);
        verify(emiasClient).getResultById("id-1");
    }
}

